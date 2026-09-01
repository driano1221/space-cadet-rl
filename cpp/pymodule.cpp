// Binding Python do ambiente. Compilado como modulo separado (spacecadet_env),
// reaproveitando os mesmos fontes do jogo.
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <cstring>
#include <pybind11/stl.h>
#include "rlenv.h"

namespace py = pybind11;

#if _WIN32
#include <windows.h>

// Mesmo adaptador de SpaceCadetPinball.cpp (que fica de fora deste alvo por
// conter o main): abre caminhos UTF-8 no Windows.
FILE* fopenu(const char* path, const char* opt)
{
	wchar_t* wideArgs[2]{};
	for (auto& arg : wideArgs)
	{
		auto src = wideArgs[0] ? opt : path;
		auto length = MultiByteToWideChar(CP_UTF8, 0, src, -1, nullptr, 0);
		arg = new wchar_t[length];
		MultiByteToWideChar(CP_UTF8, 0, src, -1, arg, length);
	}

	auto fileHandle = _wfopen(wideArgs[0], wideArgs[1]);
	for (auto arg : wideArgs)
		delete[] arg;

	return fileHandle;
}
#endif



PYBIND11_MODULE(spacecadet_env, m)
{
	m.doc() = "Space Cadet Pinball como ambiente passo-a-passo para RL";

	py::class_<rlenv::Estado>(m, "Estado")
		.def_readonly("bola_x", &rlenv::Estado::bola_x)
		.def_readonly("bola_y", &rlenv::Estado::bola_y)
		.def_readonly("bola_vx", &rlenv::Estado::bola_vx)
		.def_readonly("bola_vy", &rlenv::Estado::bola_vy)
		.def_readonly("bola_speed", &rlenv::Estado::bola_speed)
		.def_readonly("tempo_s", &rlenv::Estado::tempo_s)
		.def_readonly("score", &rlenv::Estado::score)
		.def_readonly("bolas_restantes", &rlenv::Estado::bolas_restantes)
		.def_readonly("bolas_em_jogo", &rlenv::Estado::bolas_em_jogo)
		.def_readonly("luzes_acesas", &rlenv::Estado::luzes_acesas)
		.def_readonly("rank", &rlenv::Estado::rank)
		.def_readonly("rank_total", &rlenv::Estado::rank_total)
		.def_readonly("progresso", &rlenv::Estado::progresso)
		.def_readonly("progresso_total", &rlenv::Estado::progresso_total)
		.def_readonly("combustivel", &rlenv::Estado::combustivel)
		.def_readonly("ev_mission_target", &rlenv::Estado::ev_mission_target)
		.def_readonly("ev_launch_ramp", &rlenv::Estado::ev_launch_ramp)
		.def_readonly("ev_missao_completa", &rlenv::Estado::ev_missao_completa)
		.def_readonly("ev_bumper", &rlenv::Estado::ev_bumper)
		.def_readonly("ev_hyperspace", &rlenv::Estado::ev_hyperspace)
		.def_readonly("ev_medal", &rlenv::Estado::ev_medal)
		.def_readonly("bolas_extras", &rlenv::Estado::bolas_extras)
		.def_readonly("ev_flip_acerto", &rlenv::Estado::ev_flip_acerto)
		.def_readonly("ev_extra_ganha", &rlenv::Estado::ev_extra_ganha)
		.def_readonly("nudge_count", &rlenv::Estado::nudge_count)
		.def_readonly("tilt", &rlenv::Estado::tilt)
		.def_readonly("combustivel_total", &rlenv::Estado::combustivel_total)
		.def_readonly("multiplicador", &rlenv::Estado::multiplicador)
		.def_readonly("mult_alvos", &rlenv::Estado::mult_alvos)
		.def_readonly("mult_bits", &rlenv::Estado::mult_bits)
		.def_readonly("tela_x", &rlenv::Estado::tela_x)
		.def_readonly("tela_y", &rlenv::Estado::tela_y)
		.def_readonly("flip_esq_ang", &rlenv::Estado::flip_esq_ang)
		.def_readonly("flip_dir_ang", &rlenv::Estado::flip_dir_ang)
		.def_readonly("bola_rel_esq_x", &rlenv::Estado::bola_rel_esq_x)
		.def_readonly("bola_rel_esq_y", &rlenv::Estado::bola_rel_esq_y)
		.def_readonly("bola_rel_dir_x", &rlenv::Estado::bola_rel_dir_x)
		.def_readonly("bola_rel_dir_y", &rlenv::Estado::bola_rel_dir_y)
		.def_readonly("fim", &rlenv::Estado::fim)
		.def("__repr__", [](const rlenv::Estado& e) {
			return "<Estado score=" + std::to_string(e.score) +
			       " bola=(" + std::to_string(e.bola_x) + ", " + std::to_string(e.bola_y) +
			       ") bolas=" + std::to_string(e.bolas_restantes) +
			       (e.fim ? " FIM>" : ">");
		});

	// As chamadas soltam o GIL: a thread do jogo precisa rodar em paralelo
	// e o Python fica so' esperando a resposta.
	py::class_<rlenv::Peca>(m, "Peca")
		.def_readonly("nome", &rlenv::Peca::nome)
		.def_readonly("tipo", &rlenv::Peca::tipo)
		.def_readonly("x", &rlenv::Peca::x)
		.def_readonly("y", &rlenv::Peca::y)
		.def_readonly("tela_x", &rlenv::Peca::tela_x)
		.def_readonly("tela_y", &rlenv::Peca::tela_y)
		.def_readonly("larg", &rlenv::Peca::larg)
		.def_readonly("alt", &rlenv::Peca::alt)
		.def_readonly("tem_sprite", &rlenv::Peca::tem_sprite)
		.def_readonly("aceso", &rlenv::Peca::aceso)
		.def("__repr__", [](const rlenv::Peca& p) {
			return "<Peca " + p.tipo + " '" + p.nome + "' (" +
			       std::to_string(p.tela_x) + "," + std::to_string(p.tela_y) + ")>";
		});

	m.def("capturar_tela", []() {
		auto c = rlenv::CapturarTela();
		if (c.largura == 0)
			return py::array_t<unsigned char>();
		py::array_t<unsigned char> arr({c.altura, c.largura, 3});
		std::memcpy(arr.mutable_data(), c.rgb.data(), c.rgb.size());
		return arr;
	}, "Quadro atual do jogo como array (altura, largura, 3) RGB.");

	m.def("inventario", &rlenv::Inventario,
	      "Todos os componentes da mesa, com tipo e posicao.");

	m.def("luzes_acesas", &rlenv::LuzesAcesas,
	      py::call_guard<py::gil_scoped_release>(),
	      "Estado on/off de cada luz, na ordem do inventario.");

	m.def("iniciar", &rlenv::Iniciar, py::arg("base_path") = "",
	      py::call_guard<py::gil_scoped_release>(),
	      "Sobe a thread do jogo. Chamar uma vez por processo.");
	m.def("definir_bolas", &rlenv::DefinirBolas, py::arg("n"),
	      "Bolas por partida (0 = padrao do jogo, 3).");
	m.def("definir_semente", &rlenv::DefinirSemente, py::arg("semente"),
	      "Fixa a semente aplicada a cada reset (-1 = nao fixar).");
	m.def("resetar", &rlenv::Resetar, py::call_guard<py::gil_scoped_release>(),
	      "Inicia uma partida nova e devolve o estado inicial.");
	m.def("passo", &rlenv::Passo, py::arg("flip_esq"), py::arg("flip_dir"),
	      py::arg("quadros") = 6, py::arg("nudge") = 0, py::arg("plunger") = 0,
	      py::call_guard<py::gil_scoped_release>(),
	      "Aplica as acoes e avanca `quadros` passos de fisica. "
	      "nudge: 0 nenhum, 1 esquerda, 2 direita, 3 cima. "
	      "plunger: 0 nao lancar, 1..3 forca fraca/media/forte.");
	m.def("lancar_bola", &rlenv::LancarBola, py::call_guard<py::gil_scoped_release>());
	m.def("encerrar", &rlenv::Encerrar, py::call_guard<py::gil_scoped_release>());
	m.def("ativo", &rlenv::Ativo);
}
