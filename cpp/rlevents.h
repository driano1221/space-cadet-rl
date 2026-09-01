#pragma once

// Contadores dos eventos do fluxo de missao.
//
// Recompensar "missao completa" nao funciona: o evento acontece 1 a 2 vezes por
// partida e no fim dela, onde o desconto ja anulou o credito. Estes contadores
// capturam os passos INTERMEDIARIOS, que sao frequentes e formam a cadeia ate'
// a missao - a diferenca entre premiar o gol e premiar cada passe.
namespace rlevents
{
	struct Contadores
	{
		int mission_target = 0;   // acertou alvo que seleciona missao
		int launch_ramp = 0;      // passou pela rampa de lancamento
		int missao_aceita = 0;    // missao efetivamente iniciada
		int missao_completa = 0;  // missao concluida
		int bumper = 0;           // acertou um attack bumper
		int hyperspace = 0;       // entrou no hyperspace kickout
		int medal = 0;            // derrubou um medal target
		// ExtraBalls do jogo e' um SALDO: sobe ao ganhar e desce ao usar. Ler o
		// campo no fim do episodio da' sempre zero. Aqui contamos as concessoes.
		int extra_ganha = 0;
		// Tacada de verdade: o flipper em MOVIMENTO conectou com a bola.
		// Vem do collisionFlag de TFlipper::FlipperCollision, que so' roda com
		// deltaAngle != 0 - segurar a pa' erguida nunca conta, entao premiar
		// este evento nao abre a brecha que punir o acionamento abriu.
		int flip_acerto = 0;
	};

	extern Contadores contadores;
	void Zerar();
}
