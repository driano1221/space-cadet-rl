#pragma once

#include <cstdint>
#include <string>
#include <vector>

// Ambiente passo-a-passo para RL.
//
// O jogo nao foi feito para ceder o controle: toda a inicializacao vive dentro
// de winmain::WinMain, e o loop e' dele. Em vez de refatorar isso (arriscado),
// rodamos o jogo em uma thread propria e trocamos comandos com ela por
// handshake. Assim a inicializacao testada e' reaproveitada inteira, e o
// chamador (Python) ganha um step() sincrono de verdade.

namespace rlenv
{
	struct Estado
	{
		float bola_x, bola_y;
		float bola_vx, bola_vy, bola_speed;
		float tempo_s;
		int score;
		int bolas_restantes;
		int bolas_em_jogo;
		int luzes_acesas;
		// Progressao: o jogo guarda o rank e o avanco em grupos de luzes.
		int rank;            // 0-9, de Cadet a Fleet Admiral (middle_circle)
		int rank_total;      // quantas luzes o grupo tem, para normalizar
		int progresso;       // luzes acesas no rank atual (outer_circle)
		int progresso_total;
		int combustivel;     // fuel_bargraph; missao aborta quando zera

		// Eventos do fluxo de missao, acumulados no episodio. Sao os passos
		// INTERMEDIARIOS: frequentes, ao contrario da missao completa, que
		// acontece 1 a 2 vezes por partida e nao serve de sinal de treino.
		int ev_mission_target = 0;   // acertou alvo que seleciona a missao
		int ev_launch_ramp = 0;      // passou pela rampa de lancamento
		int ev_missao_completa = 0;
		int ev_bumper = 0;
		int ev_hyperspace = 0;
		int ev_medal = 0;
		int bolas_extras = 0;     // saldo atual (sobe ao ganhar, desce ao usar)
		int ev_flip_acerto = 0;   // tacadas: flipper em movimento conectou com a bola
		int ev_extra_ganha = 0;   // quantas vezes uma bola extra foi concedida  // missao concluida

		// Medidor de abuso do nudge. Sobe a 4,0/s empurrando e desce a 1,0/s
		// parado; acima de 1,0 vem o TILT, que trava os controles e derruba a
		// bola. Sem ver isso, o agente nao tem como aprender a evitar a falta.
		float nudge_count = 0.0f;
		int tilt = 0;                // 1 = em falta, controles travados
		int no_plunger = 0;          // 1 = bola parada no plunger
		int combustivel_total;
		int multiplicador;
		// Quantos dos 3 alvos do multiplicador (a_targ7/8/9) ja estao
		// marcados. So' fechando os tres o nivel sobe - e ele cai sozinho
		// a cada 30 s, entao o que importa e' a cadencia, nao o acerto isolado.
		int mult_alvos;
		// bitmask de quais alvos estao marcados: bit0=a_targ7, 1=8, 2=9.
		// A contagem sozinha nao diz QUAL falta, e e' isso que permite mirar.
		int mult_bits;
		int tela_x, tela_y;
		// Estado dos flippers: sem isto o agente nao sabe onde a bola esta em
		// relacao a pa' nem se ela ja esta levantada - e' na pa' que o timing
		// decide a direcao e a forca da tacada.
		float flip_esq_ang, flip_dir_ang;      // 0 = parado, 1 = totalmente erguido
		float bola_rel_esq_x, bola_rel_esq_y;  // bola menos origem do flipper esq
		float bola_rel_dir_x, bola_rel_dir_y;
		bool fim;              // partida acabou (game over)
	};

	// Um componente da mesa: o que e', onde esta.
	struct Peca
	{
		std::string nome;      // GroupName do jogo
		std::string tipo;      // classe C++ resolvida por dynamic_cast
		float x, y;            // VisualPosNorm (so' para quem tem sprite)
		// Retangulo do sprite em pixels de tela. E' a posicao confiavel:
		// VisualPosNorm fica em (-1,-1) para componentes sem visual.
		int tela_x, tela_y;    // centro do sprite
		int larg, alt;         // tamanho do sprite
		bool tem_sprite;
		bool aceso;            // so' faz sentido para luzes
	};

	// Um quadro do jogo, como ele e' desenhado na tela.
	struct Captura
	{
		int largura = 0, altura = 0;
		std::vector<unsigned char> rgb;   // largura*altura*3
	};

	// Copia o framebuffer que o jogo acabou de compor (render::vscreen).
	// Diferente do bitmap estatico da mesa, inclui flippers, luzes e sprites.
	Captura CapturarTela();

	// Inventario da mesa: todos os componentes com tipo e posicao.
	// Estatico - chamar uma vez e guardar.
	std::vector<Peca> Inventario();

	// Estado dinamico das luzes, na mesma ordem em que aparecem no Inventario
	// (apenas as pecas de tipo "luz" ou "rollover_luz"). Barato o bastante
	// para chamar a cada passo.
	std::vector<uint8_t> LuzesAcesas();

	// Sobe a thread do jogo e espera ela ficar pronta. Chamar uma vez.
	bool Iniciar(const char* basePath);
	// Comeca uma partida nova; devolve o estado inicial.
	Estado Resetar();
	void DefinirSemente(int semente);   // < 0 = nao fixar
	void DefinirBolas(int n);           // 0 = padrao do jogo (3)
	int BolasConfiguradas();
	// Aplica as acoes e avanca `quadros` passos de fisica.
	// nudge: 0 = nenhum, 1 = esquerda, 2 = direita, 3 = cima
	// plunger: 0 = nao lancar, 1..3 = forca fraca/media/forte
	Estado Passo(bool flipEsq, bool flipDir, int quadros,
	             int nudge = 0, int plunger = 0);
	// Solta o plunger.
	void LancarBola();
	// Encerra a thread do jogo.
	void Encerrar();
	bool Ativo();

	// Chamado de dentro do jogo (rlmode) quando o modo embed esta ligado:
	// cede o controle e fica atendendo comandos ate' receber "parar".
	void AtenderComandos();
}
