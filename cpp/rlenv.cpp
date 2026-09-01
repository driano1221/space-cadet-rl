#include "pch.h"
#include "rlenv.h"
#include <cstdlib>

#include <atomic>
#include <condition_variable>
#include <mutex>
#include <string>
#include <thread>

#include "pb.h"
#include "proj.h"
#include "winmain.h"
#include "TPinballTable.h"
#include "TPinballComponent.h"
#include "TBall.h"
#include "TLightGroup.h"
#include "TLightBargraph.h"
#include "TLight.h"
#include "TPopupTarget.h"
#include "TFlipper.h"
#include "TFlipperEdge.h"
#include "TBumper.h"
#include "TPopupTarget.h"
#include "TSoloTarget.h"
#include "TRollover.h"
#include "TLightRollover.h"
#include "TRamp.h"
#include "TKickout.h"
#include "TSink.h"
#include "THole.h"
#include "TFlagSpinner.h"
#include "TGate.h"
#include "TOneway.h"
#include "TWall.h"
#include "TBlocker.h"
#include "TTripwire.h"
#include "TKickback.h"
#include "TDrain.h"
#include "TPlunger.h"
#include "render.h"
#include "rlevents.h"
#include "nudge.h"
#include "TPlunger.h"

namespace
{
	// Cache dos grupos de luzes que carregam a progressao. Resolvido uma vez
	// por partida: find_component varre a lista inteira de componentes.
	TLightGroup* g_rank = nullptr;
	TLightGroup* g_progresso = nullptr;
	TLightGroup* g_combustivel = nullptr;

	TLightGroup* GrupoDeLuzes(const char* nome)
	{
		if (!pb::MainTable)
			return nullptr;
		return dynamic_cast<TLightGroup*>(pb::MainTable->find_component(nome));
	}

	void ResolverGrupos()
	{
		g_rank = GrupoDeLuzes("middle_circle");
		g_progresso = GrupoDeLuzes("outer_circle");
		g_combustivel = GrupoDeLuzes("fuel_bargraph");
	}

	// Quantas luzes acesas / quantas existem no grupo.
	void ContarLuzes(TLightGroup* g, int& acesas, int& total)
	{
		if (!g)
		{
			acesas = total = 0;
			return;
		}
		acesas = g->Message(MessageCode::TLightGroupGetOnCount, 0.0f);
		total = g->Message(MessageCode::TLightGroupGetLightCount, 0.0f);
	}
}


namespace
{
	enum class Cmd { Nenhum, Passo, Resetar, Lancar, Parar, Capturar };

	// semente aplicada a cada reset; < 0 mantem o comportamento antigo
	int sementeReset = -1;

	// IDEIA 3 - curriculo de bolas: mais bolas dao tempo para aprender as
	// sequencias longas sem morrer no meio. 0 = manter o padrao do jogo (3).
	int bolasPorPartida = 0;

	struct Canal
	{
		std::mutex m;
		std::condition_variable paraJogo, paraChamador;
		Cmd comando = Cmd::Nenhum;
		rlenv::Captura captura;
		bool respostaPronta = false;
		bool jogoPronto = false;

		bool flipEsq = false, flipDir = false;
		int quadros = 1;
		int nudgeCmd = 0, plungerCmd = 0;
		rlenv::Estado estado{};
	};

	Canal canal;
	std::thread threadJogo;
	std::atomic<bool> ativo{false};

	// Estado dos flippers do lado do jogo, para so' enviar mensagem na mudanca.
	bool estadoEsq = false, estadoDir = false;
	// passos restantes segurando o plunger (0 = solto)
	int plungerSegurar = 0;
	int passosEpisodio = 0;
	int scoreAnterior = -1;
	int passosEstagnado = 0;
	constexpr float kPassoMs = 1000.0f / 120.0f;
	// Depois de perder uma bola o jogo fica esperando o plunger. Sem relancar,
	// a partida trava e o tempo passa sem pontuar. Mesmo criterio do rlmode.
	constexpr int kEstagnadoMax = 120 * 3;

	void Msg(MessageCode code)
	{
		if (pb::MainTable)
			pb::MainTable->Message(code, pb::time_now);
	}

	void AplicarFlippers(bool esq, bool dir)
	{
		if (esq != estadoEsq)
		{
			Msg(esq ? MessageCode::LeftFlipperInputPressed : MessageCode::LeftFlipperInputReleased);
			estadoEsq = esq;
		}
		if (dir != estadoDir)
		{
			Msg(dir ? MessageCode::RightFlipperInputPressed : MessageCode::RightFlipperInputReleased);
			estadoDir = dir;
		}
	}

	// Bola posicionada no canal do plunger (extrema esquerda em coordenadas
	// da mesa), pronta para ser lancada.
	bool BolaNoPlunger()
	{
		auto* t = pb::MainTable;
		if (!t || t->BallList.empty() || !t->BallList[0])
			return false;
		const auto& p = t->BallList[0]->Position;
		return p.X < -6.5f && p.Y > 5.0f;
	}

	// Bola fora do canal de lancamento, ou seja, em jogo de fato.
	bool BolaEmJogo()
	{
		auto* t = pb::MainTable;
		if (!t || t->BallList.empty() || !t->BallList[0])
			return false;
		const auto& p = t->BallList[0]->Position;
		return !(p.X == 0.0f && p.Y == 0.0f) && p.X > -6.5f;
	}

	rlenv::Estado LerEstado()
	{
		rlenv::Estado e{};
		auto* t = pb::MainTable;
		if (!t)
		{
			e.fim = true;
			return e;
		}

		// ActiveFlag nao indica "bola em jogo" (o TEdgeSegment o usa como
		// flag temporario), entao lemos sempre a primeira bola da lista.
		TBall* bola = t->BallList.empty() ? nullptr : t->BallList[0];
		for (auto* b : t->BallList)
			if (b && b->ActiveFlag)
				e.bolas_em_jogo++;

		if (bola)
		{
			e.bola_x = bola->Position.X;
			e.bola_y = bola->Position.Y;
			e.bola_vx = bola->Direction.X * bola->Speed;
			e.bola_vy = bola->Direction.Y * bola->Speed;
			e.bola_speed = bola->Speed;
			const auto tela = proj::xform_to_2d(bola->Position);
			e.tela_x = tela.X;
			e.tela_y = tela.Y;
		}
		else
		{
			e.tela_x = e.tela_y = -1;
		}

		if (t->LightGroup)
			for (auto* l : t->LightGroup->List)
				if (l && l->LightOnFlag)
					e.luzes_acesas++;

		// Progressao: rank, avanco dentro do rank e combustivel.
		ContarLuzes(g_rank, e.rank, e.rank_total);
		ContarLuzes(g_progresso, e.progresso, e.progresso_total);
		ContarLuzes(g_combustivel, e.combustivel, e.combustivel_total);

		// Eventos do fluxo de missao, contados dentro dos controllers do jogo.
		e.ev_mission_target = rlevents::contadores.mission_target;
		e.ev_launch_ramp = rlevents::contadores.launch_ramp;
		e.ev_missao_completa = rlevents::contadores.missao_completa;
		e.ev_bumper = rlevents::contadores.bumper;
		e.ev_hyperspace = rlevents::contadores.hyperspace;
		e.ev_medal = rlevents::contadores.medal;
		e.bolas_extras = t->ExtraBalls;
		e.ev_flip_acerto = rlevents::contadores.flip_acerto;
		e.ev_extra_ganha = rlevents::contadores.extra_ganha;
		e.nudge_count = nudge::nudge_count;
		e.tilt = pb::MainTable && pb::MainTable->TiltLockFlag ? 1 : 0;

		// angulo e posicao de cada flipper
		auto lerFlipper = [&](TFlipper* f, float& ang, float& relx, float& rely)
		{
			if (!f || !f->FlipperEdge)
				return;
			auto* fe = f->FlipperEdge;
			ang = fe->AngleMax != 0.0f ? fe->CurrentAngle / fe->AngleMax : 0.0f;
			if (bola)
			{
				relx = bola->Position.X - fe->RotOrigin.X;
				rely = bola->Position.Y - fe->RotOrigin.Y;
			}
		};
		lerFlipper(t->FlipperL, e.flip_esq_ang, e.bola_rel_esq_x, e.bola_rel_esq_y);
		lerFlipper(t->FlipperR, e.flip_dir_ang, e.bola_rel_dir_x, e.bola_rel_dir_y);

		e.score = t->CurScore;
		e.bolas_restantes = t->BallCount;
		e.multiplicador = t->ScoreMultiplier;
		e.mult_alvos = 0;
		e.mult_bits = 0;
		{
			const char* nomes[3] = {"a_targ7", "a_targ8", "a_targ9"};
			for (int i = 0; i < 3; i++)
				if (auto* alvo = t->find_component(nomes[i]))
					if (alvo->MessageField)
					{
						e.mult_alvos++;
						e.mult_bits |= (1 << i);
					}
		}
		e.tempo_s = passosEpisodio * kPassoMs / 1000.0f;
		e.fim = pb::game_mode != GameModes::InGame;
		return e;
	}
}

// ---------------------------------------------------------------- lado do jogo

void rlenv::AtenderComandos()
{
	{
		std::lock_guard<std::mutex> lk(canal.m);
		canal.jogoPronto = true;
	}
	canal.paraChamador.notify_all();

	for (;;)
	{
		std::unique_lock<std::mutex> lk(canal.m);
		canal.paraJogo.wait(lk, [] { return canal.comando != Cmd::Nenhum; });
		const Cmd cmd = canal.comando;
		const bool esq = canal.flipEsq, dir = canal.flipDir;
		const int quadros = canal.quadros;
		lk.unlock();

		if (cmd == Cmd::Parar)
		{
			std::lock_guard<std::mutex> g(canal.m);
			canal.comando = Cmd::Nenhum;
			canal.respostaPronta = true;
			canal.paraChamador.notify_all();
			return;
		}

		if (cmd == Cmd::Resetar)
		{
			// RandFloat() usa std::rand(): fixando a semente aqui, a mesma
			// sequencia de acoes reproduz o mesmo episodio. Sem isto o replay
			// diverge e nao da' para voltar a um estado promissor (Go-Explore),
			// nem parear avaliacoes de verdade. semente < 0 = nao mexer.
			if (sementeReset >= 0)
				std::srand(static_cast<unsigned>(sementeReset));
			// o construtor da mesa roda uma vez so'; para o curriculo valer em
			// toda partida, MaxBallCount tem de ser reaplicado a cada reset
			if (bolasPorPartida > 0 && pb::MainTable)
				pb::MainTable->MaxBallCount = bolasPorPartida;
			rlevents::Zerar();
			nudge::Zerar();   // senao o timer do nudge atravessa o reset
			plungerSegurar = 0;
			estadoEsq = estadoDir = false;
			passosEpisodio = 0;
			scoreAnterior = -1;
			passosEstagnado = 0;
			pb::replay_level(false);
			ResolverGrupos();

			// Tres tempos que precisam ser respeitados aqui, e cada um
			// custou depuracao:
			//  1. a bola nao existe no instante do replay_level;
			//  2. leva ~1 s de jogo ate' ser posicionada no canal do plunger;
			//  3. ainda desliza canal abaixo por mais ~1 s, e o plunger so'
			//     lanca depois que ela assenta no fundo.
			// Um laco unico cobre os tres: insiste no launch ate' a bola
			// estar de fato em jogo, fora do canal.
			for (int i = 0; i < 900 && !BolaEmJogo(); i++)
			{
				if (i % 30 == 0)
					pb::launch_ball();
				pb::frame(kPassoMs);
				passosEpisodio++;
			}
		}
		else if (cmd == Cmd::Lancar)
		{
			pb::launch_ball();
		}
		else if (cmd == Cmd::Capturar)
		{
			// render::update() ja rodou no ultimo passo, entao o vscreen
			// contem o quadro atual, com tudo desenhado.
			auto* vs = render::vscreen;
			auto& cap = canal.captura;
			cap.largura = cap.altura = 0;
			cap.rgb.clear();
			if (vs && vs->BmpBufPtr1 && vs->Width > 0 && vs->Height > 0)
			{
				cap.largura = vs->Width;
				cap.altura = vs->Height;
				cap.rgb.resize(static_cast<size_t>(vs->Width) * vs->Height * 3);
				for (int y = 0; y < vs->Height; y++)
				{
					const ColorRgba* linha = vs->BmpBufPtr1 + static_cast<size_t>(y) * vs->Stride;
					unsigned char* dst = cap.rgb.data() + static_cast<size_t>(y) * vs->Width * 3;
					for (int x = 0; x < vs->Width; x++)
					{
						dst[x * 3 + 0] = linha[x].GetRed();
						dst[x * 3 + 1] = linha[x].GetGreen();
						dst[x * 3 + 2] = linha[x].GetBlue();
					}
				}
			}
		}
		else if (cmd == Cmd::Passo)
		{
			// nudge: uma direcao por passo. O jogo reverte sozinho em 0,4 s.
			switch (canal.nudgeCmd)
			{
			case 1: nudge::nudge_left(); break;
			case 2: nudge::nudge_right(); break;
			case 3: nudge::nudge_up(); break;
			default: break;
			}
			// Plunger modulado. Nao adianta escrever em Boost: ele so' cresce
			// pelo timer de pullback enquanto o botao esta pressionado, e
			// PlungerInputReleased ignora tudo se PullbackStartedFlag estiver
			// desligado. A unica forma e' fazer o que um humano faz - segurar
			// por um tempo e soltar.
			if (canal.plungerCmd > 0 && pb::MainTable && pb::MainTable->Plunger
			    && plungerSegurar == 0)
			{
				// quantos passos segurar: quanto mais, maior a carga
				const int passos[4] = {0, 4, 10, 22};
				plungerSegurar = passos[canal.plungerCmd];
				pb::MainTable->Plunger->Message(MessageCode::PlungerInputPressed, 0.0f);
			}
			if (plungerSegurar > 0 && --plungerSegurar == 0 && pb::MainTable
			    && pb::MainTable->Plunger)
			{
				pb::MainTable->Plunger->Message(MessageCode::PlungerInputReleased, 0.0f);
			}
			AplicarFlippers(esq, dir);
			for (int i = 0; i < quadros && pb::game_mode == GameModes::InGame; i++)
			{
				pb::frame(kPassoMs);
				passosEpisodio++;

				const int sc = pb::MainTable ? pb::MainTable->CurScore : 0;
				if (sc != scoreAnterior)
				{
					scoreAnterior = sc;
					passosEstagnado = 0;
				}
				else if (++passosEstagnado > kEstagnadoMax)
				{
					pb::launch_ball();      // bola presa ou esperando o plunger
					passosEstagnado = 0;
				}
			}
		}

		const auto e = LerEstado();
		{
			std::lock_guard<std::mutex> g(canal.m);
			canal.estado = e;
			canal.comando = Cmd::Nenhum;
			canal.respostaPronta = true;
		}
		canal.paraChamador.notify_all();
	}
}

// ------------------------------------------------------------ lado do chamador

namespace
{
	rlenv::Estado Enviar(Cmd cmd, bool esq = false, bool dir = false, int quadros = 1,
	                     int nudge = 0, int plunger = 0)
	{
		std::unique_lock<std::mutex> lk(canal.m);
		canal.nudgeCmd = nudge;
		canal.plungerCmd = plunger;
		canal.comando = cmd;
		canal.flipEsq = esq;
		canal.flipDir = dir;
		canal.quadros = quadros;
		canal.respostaPronta = false;
		canal.paraJogo.notify_all();
		canal.paraChamador.wait(lk, [] { return canal.respostaPronta; });
		canal.respostaPronta = false;
		return canal.estado;
	}
}

std::vector<rlenv::Peca> rlenv::Inventario()
{
	std::vector<Peca> pecas;
	auto* t = pb::MainTable;
	if (!t)
		return pecas;

	// Ordem importa: as classes mais especificas vem primeiro, porque varias
	// herdam de TCollisionComponent.
	auto classificar = [](TPinballComponent* c) -> const char*
	{
		if (dynamic_cast<TBumper*>(c))        return "bumper";
		if (dynamic_cast<TPopupTarget*>(c))   return "alvo_popup";
		if (dynamic_cast<TSoloTarget*>(c))    return "alvo_solo";
		if (dynamic_cast<TLightRollover*>(c)) return "rollover_luz";
		if (dynamic_cast<TRollover*>(c))      return "rollover";
		if (dynamic_cast<TRamp*>(c))          return "rampa";
		if (dynamic_cast<TKickout*>(c))       return "kickout";
		if (dynamic_cast<TSink*>(c))          return "sink";
		if (dynamic_cast<THole*>(c))          return "buraco";
		if (dynamic_cast<TFlagSpinner*>(c))   return "spinner";
		if (dynamic_cast<TKickback*>(c))      return "kickback";
		if (dynamic_cast<TGate*>(c))          return "portao";
		if (dynamic_cast<TOneway*>(c))        return "mao_unica";
		if (dynamic_cast<TBlocker*>(c))       return "bloqueador";
		if (dynamic_cast<TTripwire*>(c))      return "tripwire";
		if (dynamic_cast<TFlipper*>(c))       return "flipper";
		if (dynamic_cast<TDrain*>(c))         return "dreno";
		if (dynamic_cast<TPlunger*>(c))       return "plunger";
		if (dynamic_cast<TBall*>(c))          return "bola";
		if (dynamic_cast<TLight*>(c))         return "luz";
		if (dynamic_cast<TWall*>(c))          return "parede";
		return "outro";
	};

	for (auto* c : t->ComponentList)
	{
		if (!c)
			continue;
		Peca p;
		p.nome = c->GroupName ? c->GroupName : "";
		p.tipo = classificar(c);
		const auto v = c->get_coordinates();
		p.x = v.X;
		p.y = v.Y;

		// A posicao boa vem do retangulo do sprite, em pixels de tela.
		p.tem_sprite = c->RenderSprite != nullptr;
		if (p.tem_sprite)
		{
			const auto& r = c->RenderSprite->BmpRect;
			p.tela_x = r.XPosition + r.Width / 2;
			p.tela_y = r.YPosition + r.Height / 2;
			p.larg = r.Width;
			p.alt = r.Height;
		}
		else
		{
			p.tela_x = p.tela_y = -1;
			p.larg = p.alt = 0;
		}
		auto* luz = dynamic_cast<TLight*>(c);
		p.aceso = luz && luz->LightOnFlag;
		pecas.push_back(p);
	}
	return pecas;
}

std::vector<uint8_t> rlenv::LuzesAcesas()
{
	std::vector<uint8_t> estado;
	auto* t = pb::MainTable;
	if (!t)
		return estado;
	for (auto* c : t->ComponentList)
	{
		auto* luz = dynamic_cast<TLight*>(c);
		if (luz)
			estado.push_back(luz->LightOnFlag ? 1 : 0);
	}
	return estado;
}

bool rlenv::Iniciar(const char* basePath)
{
	if (ativo)
		return true;

	static std::string args;
	args = "-rl-embed";
	if (basePath && basePath[0])
		args += std::string(" -bp ") + basePath;

	threadJogo = std::thread([] { winmain::WinMain(args.c_str()); });

	std::unique_lock<std::mutex> lk(canal.m);
	const bool ok = canal.paraChamador.wait_for(lk, std::chrono::seconds(30),
	                                            [] { return canal.jogoPronto; });
	ativo = ok;
	if (!ok && threadJogo.joinable())
		threadJogo.detach();
	return ok;
}

void rlenv::DefinirSemente(int semente) { sementeReset = semente; }

void rlenv::DefinirBolas(int n) { bolasPorPartida = n; }

int rlenv::BolasConfiguradas() { return bolasPorPartida; }

rlenv::Estado rlenv::Resetar() { return Enviar(Cmd::Resetar); }
rlenv::Estado rlenv::Passo(bool e, bool d, int q, int nudge, int plunger)
{
	return Enviar(Cmd::Passo, e, d, q, nudge, plunger);
}
void rlenv::LancarBola() { Enviar(Cmd::Lancar); }

rlenv::Captura rlenv::CapturarTela()
{
	// Enviar() so' retorna depois que a thread do jogo terminou o comando,
	// entao o buffer ja esta estavel aqui.
	Enviar(Cmd::Capturar);
	std::lock_guard<std::mutex> lk(canal.m);
	return canal.captura;
}
bool rlenv::Ativo() { return ativo; }

void rlenv::Encerrar()
{
	if (!ativo)
		return;
	Enviar(Cmd::Parar);
	ativo = false;
	if (threadJogo.joinable())
		threadJogo.join();
}
