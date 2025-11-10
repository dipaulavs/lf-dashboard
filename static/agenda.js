/**
 * Sistema de Agenda de Visitas
 * Gerenciamento completo de agendamentos
 */

console.log('📄 agenda.js - Arquivo carregado (topo do arquivo)');

const API_BASE = '';
let agendamentos = [];
let imoveisParaAgenda = [];
let agendamentoEmEdicao = null;

// ==================== INICIALIZAÇÃO ====================

// Flag para evitar inicialização dupla
window.agendaInitialized = false;

console.log('🔧 agenda.js - Variáveis inicializadas');

// Inicializar assim que documento carregar (antes do tab system)
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 [AGENDA] DOMContentLoaded disparado');
    console.log('🔍 [AGENDA] Estado inicial:', {
        agendaInitialized: window.agendaInitialized,
        timestamp: new Date().toLocaleTimeString()
    });

    // Aguardar um pouco para garantir que HTML está carregado
    setTimeout(() => {
        console.log('⏰ [AGENDA] Timeout 500ms completado - iniciando...');
        initAgenda();
    }, 500);
});

console.log('✅ [AGENDA] Event listener DOMContentLoaded registrado');

function initAgenda() {
    console.log('═══════════════════════════════════════');
    console.log('🔥 [AGENDA] initAgenda() CHAMADA');
    console.log('═══════════════════════════════════════');

    if (window.agendaInitialized) {
        console.log('⚠️ [AGENDA] Agenda já inicializada, pulando...');
        return;
    }

    console.log('📍 [AGENDA] Buscando elementos do DOM...');

    // Event listeners com verificação
    const btnNovaVisita = document.getElementById('btnNovaVisita');
    const btnFecharModalVisita = document.getElementById('btnFecharModalVisita');
    const btnCancelarVisita = document.getElementById('btnCancelarVisita');
    const formVisita = document.getElementById('formVisita');
    const btnSalvarObservacoes = document.getElementById('btnSalvarObservacoes');
    const filterStatusAgenda = document.getElementById('filterStatusAgenda');
    const filterDataInicio = document.getElementById('filterDataInicio');
    const filterDataFim = document.getElementById('filterDataFim');

    console.log('🔍 [AGENDA] Elementos encontrados:', {
        btnNovaVisita: !!btnNovaVisita,
        btnFecharModalVisita: !!btnFecharModalVisita,
        btnCancelarVisita: !!btnCancelarVisita,
        formVisita: !!formVisita,
        btnSalvarObservacoes: !!btnSalvarObservacoes,
        filterStatusAgenda: !!filterStatusAgenda,
        filterDataInicio: !!filterDataInicio,
        filterDataFim: !!filterDataFim
    });

    if (btnNovaVisita) {
        console.log('🔧 [AGENDA] Configurando event listener para btnNovaVisita...');
        btnNovaVisita.addEventListener('click', (e) => {
            console.log('═══════════════════════════════════════');
            console.log('🖱️ [AGENDA] BOTÃO NOVA VISITA CLICADO!');
            console.log('═══════════════════════════════════════');
            e.preventDefault();
            abrirModalNovaVisita();
        });
        console.log('✅ [AGENDA] Event listener btnNovaVisita configurado');

        // Testar se o botão está visível
        const btnStyle = window.getComputedStyle(btnNovaVisita);
        console.log('👁️ [AGENDA] Visibilidade btnNovaVisita:', {
            display: btnStyle.display,
            visibility: btnStyle.visibility,
            opacity: btnStyle.opacity,
            pointerEvents: btnStyle.pointerEvents
        });
    } else {
        console.error('❌ [AGENDA] btnNovaVisita NÃO ENCONTRADO!');
    }

    if (btnFecharModalVisita) {
        btnFecharModalVisita.addEventListener('click', fecharModalVisita);
        console.log('✅ [AGENDA] Event listener btnFecharModalVisita configurado');
    }

    if (btnCancelarVisita) {
        btnCancelarVisita.addEventListener('click', fecharModalVisita);
        console.log('✅ [AGENDA] Event listener btnCancelarVisita configurado');
    }

    if (formVisita) {
        formVisita.addEventListener('submit', salvarVisita);
        console.log('✅ [AGENDA] Event listener formVisita configurado');
    }

    if (btnSalvarObservacoes) {
        console.log('🔧 [AGENDA] Configurando event listener para btnSalvarObservacoes...');
        btnSalvarObservacoes.addEventListener('click', (e) => {
            console.log('═══════════════════════════════════════');
            console.log('🖱️ [AGENDA] BOTÃO SALVAR OBSERVAÇÕES CLICADO!');
            console.log('═══════════════════════════════════════');
            e.preventDefault();
            salvarObservacoes();
        });
        console.log('✅ [AGENDA] Event listener btnSalvarObservacoes configurado');

        // Testar se o botão está visível
        const btnStyle = window.getComputedStyle(btnSalvarObservacoes);
        console.log('👁️ [AGENDA] Visibilidade btnSalvarObservacoes:', {
            display: btnStyle.display,
            visibility: btnStyle.visibility,
            opacity: btnStyle.opacity,
            pointerEvents: btnStyle.pointerEvents
        });
    } else {
        console.error('❌ [AGENDA] btnSalvarObservacoes NÃO ENCONTRADO!');
    }

    if (filterStatusAgenda) {
        filterStatusAgenda.addEventListener('change', aplicarFiltrosAgenda);
        console.log('✅ [AGENDA] Event listener filterStatusAgenda configurado');
    }

    if (filterDataInicio) {
        filterDataInicio.addEventListener('change', aplicarFiltrosAgenda);
        console.log('✅ [AGENDA] Event listener filterDataInicio configurado');
    }

    if (filterDataFim) {
        filterDataFim.addEventListener('change', aplicarFiltrosAgenda);
        console.log('✅ [AGENDA] Event listener filterDataFim configurado');
    }

    console.log('📊 [AGENDA] Carregando dados iniciais...');

    // Carregar dados iniciais
    carregarObservacoes();
    carregarImoveisParaAgenda();
    carregarAgendamentos();
    carregarEstatisticasAgenda();

    // Marcar como inicializado
    window.agendaInitialized = true;
    console.log('═══════════════════════════════════════');
    console.log('✅ [AGENDA] INICIALIZAÇÃO COMPLETA!');
    console.log('═══════════════════════════════════════');
}

// ==================== MODAL ====================

function abrirModalNovaVisita() {
    console.log('📅 abrirModalNovaVisita chamado');

    agendamentoEmEdicao = null;

    const modalVisitaTitle = document.getElementById('modalVisitaTitle');
    const formVisita = document.getElementById('formVisita');
    const visitaData = document.getElementById('visitaData');
    const modalVisita = document.getElementById('modalVisita');

    if (!modalVisitaTitle || !formVisita || !visitaData || !modalVisita) {
        console.error('❌ Elementos do modal não encontrados');
        return;
    }

    modalVisitaTitle.textContent = 'Nova Visita';
    formVisita.reset();

    // Definir data mínima como hoje
    const hoje = new Date().toISOString().split('T')[0];
    visitaData.min = hoje;

    // Popular select de imóveis
    popularSelectImoveis();

    modalVisita.style.display = 'flex';
    console.log('✅ Modal aberto');
}

function fecharModalVisita() {
    document.getElementById('modalVisita').style.display = 'none';
    agendamentoEmEdicao = null;
}

function popularSelectImoveis() {
    const select = document.getElementById('visitaImovelId');
    select.innerHTML = '<option value="">Selecione um imóvel</option>';

    imoveisParaAgenda.forEach(imovel => {
        const option = document.createElement('option');
        option.value = imovel.id;
        option.textContent = `${imovel.titulo} - ${imovel.cidade}`;
        select.appendChild(option);
    });
}

// ==================== CRUD ====================

async function carregarImoveisParaAgenda() {
    try {
        const response = await fetch(`${API_BASE}/api/imoveis?status=disponivel`, {
            headers: {
                'Authorization': 'Bearer dev-token-12345'
            }
        });

        const data = await response.json();
        if (data.success) {
            imoveisParaAgenda = data.imoveis;
        }
    } catch (error) {
        console.error('Erro ao carregar imóveis:', error);
    }
}

async function carregarAgendamentos() {
    try {
        const filtros = obterFiltrosAgenda();
        const queryString = new URLSearchParams(filtros).toString();

        const response = await fetch(`${API_BASE}/api/agenda/agendamentos?${queryString}`);
        const data = await response.json();

        if (data.success) {
            agendamentos = data.agendamentos;
            renderizarTabelaAgenda();
        }
    } catch (error) {
        console.error('Erro ao carregar agendamentos:', error);
        mostrarErroTabela('Erro ao carregar agendamentos');
    }
}

async function salvarVisita(e) {
    e.preventDefault();

    const dados = {
        nome_cliente: document.getElementById('visitaNome').value,
        whatsapp: document.getElementById('visitaWhatsApp').value,
        imovel_id: parseInt(document.getElementById('visitaImovelId').value),
        data_visita: document.getElementById('visitaData').value,
        hora_visita: document.getElementById('visitaHora').value,
        status: document.getElementById('visitaStatus').value,
        observacoes: document.getElementById('visitaObservacoes').value || null
    };

    try {
        let response;

        if (agendamentoEmEdicao) {
            // Atualizar
            response = await fetch(`${API_BASE}/api/agenda/agendamentos/${agendamentoEmEdicao}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(dados)
            });
        } else {
            // Criar
            response = await fetch(`${API_BASE}/api/agenda/agendamentos`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(dados)
            });
        }

        const result = await response.json();

        if (result.success) {
            alert(agendamentoEmEdicao ? 'Visita atualizada com sucesso!' : 'Visita agendada com sucesso!');
            fecharModalVisita();
            carregarAgendamentos();
            carregarEstatisticasAgenda();
        } else {
            alert('Erro: ' + result.error);
        }
    } catch (error) {
        console.error('Erro ao salvar visita:', error);
        alert('Erro ao salvar visita');
    }
}

async function editarAgendamento(id) {
    const agendamento = agendamentos.find(a => a.id === id);
    if (!agendamento) return;

    agendamentoEmEdicao = id;
    document.getElementById('modalVisitaTitle').textContent = 'Editar Visita';

    // Preencher formulário
    document.getElementById('visitaNome').value = agendamento.nome_cliente;
    document.getElementById('visitaWhatsApp').value = agendamento.whatsapp;
    document.getElementById('visitaImovelId').value = agendamento.imovel_id;
    document.getElementById('visitaData').value = agendamento.data_visita;
    document.getElementById('visitaHora').value = agendamento.hora_visita;
    document.getElementById('visitaStatus').value = agendamento.status;
    document.getElementById('visitaObservacoes').value = agendamento.observacoes || '';

    popularSelectImoveis();
    document.getElementById('modalVisita').style.display = 'flex';
}

async function deletarAgendamento(id) {
    if (!confirm('Tem certeza que deseja deletar este agendamento?')) return;

    try {
        const response = await fetch(`${API_BASE}/api/agenda/agendamentos/${id}`, {
            method: 'DELETE'
        });

        const result = await response.json();

        if (result.success) {
            alert('Agendamento deletado com sucesso!');
            carregarAgendamentos();
            carregarEstatisticasAgenda();
        } else {
            alert('Erro: ' + result.error);
        }
    } catch (error) {
        console.error('Erro ao deletar agendamento:', error);
        alert('Erro ao deletar agendamento');
    }
}

// ==================== OBSERVAÇÕES ====================

async function carregarObservacoes() {
    try {
        const response = await fetch(`${API_BASE}/api/agenda/observacoes`);
        const data = await response.json();

        if (data.success) {
            document.getElementById('agendaObservacoes').value = data.observacoes;
        }
    } catch (error) {
        console.error('Erro ao carregar observações:', error);
    }
}

async function salvarObservacoes() {
    console.log('💾 salvarObservacoes chamado');

    const agendaObservacoes = document.getElementById('agendaObservacoes');

    if (!agendaObservacoes) {
        console.error('❌ Campo agendaObservacoes não encontrado');
        alert('Erro: Campo de observações não encontrado');
        return;
    }

    const observacoes = agendaObservacoes.value;
    console.log('📝 Observações:', observacoes);

    try {
        const response = await fetch(`${API_BASE}/api/agenda/observacoes`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ observacoes })
        });

        const result = await response.json();
        console.log('📡 Resposta do servidor:', result);

        if (result.success) {
            alert('Observações salvas com sucesso!');
            console.log('✅ Observações salvas');
        } else {
            alert('Erro: ' + result.error);
            console.error('❌ Erro ao salvar:', result.error);
        }
    } catch (error) {
        console.error('❌ Erro ao salvar observações:', error);
        alert('Erro ao salvar observações: ' + error.message);
    }
}

// ==================== ESTATÍSTICAS ====================

async function carregarEstatisticasAgenda() {
    try {
        const response = await fetch(`${API_BASE}/api/agenda/estatisticas`);
        const data = await response.json();

        if (data.success) {
            const stats = data.estatisticas;
            document.getElementById('totalVisitas').textContent = stats.total;
            document.getElementById('visitasHoje').textContent = stats.hoje;
            document.getElementById('visitasProximos7').textContent = stats.proximos_7_dias;
        }
    } catch (error) {
        console.error('Erro ao carregar estatísticas:', error);
    }
}

// ==================== FILTROS ====================

function obterFiltrosAgenda() {
    const filtros = {};

    const status = document.getElementById('filterStatusAgenda').value;
    if (status !== 'all') {
        filtros.status = status;
    }

    const dataInicio = document.getElementById('filterDataInicio').value;
    if (dataInicio) {
        filtros.data_inicio = dataInicio;
    }

    const dataFim = document.getElementById('filterDataFim').value;
    if (dataFim) {
        filtros.data_fim = dataFim;
    }

    return filtros;
}

function aplicarFiltrosAgenda() {
    carregarAgendamentos();
}

// ==================== RENDERIZAÇÃO ====================

function renderizarTabelaAgenda() {
    const tbody = document.getElementById('agendaBody');

    if (agendamentos.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="loading">Nenhum agendamento encontrado</td></tr>';
        return;
    }

    tbody.innerHTML = agendamentos.map(agendamento => {
        const imovel = imoveisParaAgenda.find(i => i.id === agendamento.imovel_id);
        const imovelNome = imovel ? imovel.titulo : `ID ${agendamento.imovel_id}`;

        const statusEmoji = {
            'agendado': '⏳',
            'confirmado': '✅',
            'realizado': '🎉',
            'cancelado': '❌'
        };

        const dataHora = formatarDataHora(agendamento.data_visita, agendamento.hora_visita);

        return `
            <tr>
                <td>${dataHora}</td>
                <td>${agendamento.nome_cliente}</td>
                <td>${formatarWhatsApp(agendamento.whatsapp)}</td>
                <td>${imovelNome}</td>
                <td>${statusEmoji[agendamento.status]} ${capitalize(agendamento.status)}</td>
                <td>${agendamento.observacoes || '-'}</td>
                <td>
                    <button class="btn-action" onclick="editarAgendamento(${agendamento.id})" title="Editar">✏️</button>
                    <button class="btn-action" onclick="deletarAgendamento(${agendamento.id})" title="Deletar">🗑️</button>
                </td>
            </tr>
        `;
    }).join('');
}

function mostrarErroTabela(mensagem) {
    const tbody = document.getElementById('agendaBody');
    tbody.innerHTML = `<tr><td colspan="7" class="loading">${mensagem}</td></tr>`;
}

// ==================== UTILIDADES ====================

function formatarDataHora(data, hora) {
    const dataObj = new Date(data + 'T00:00:00');
    const dataFormatada = dataObj.toLocaleDateString('pt-BR');
    return `${dataFormatada} às ${hora}`;
}

function formatarWhatsApp(whatsapp) {
    // Formata: 5531999887766 -> +55 31 99988-7766
    if (whatsapp.length === 13) {
        return `+${whatsapp.slice(0, 2)} ${whatsapp.slice(2, 4)} ${whatsapp.slice(4, 9)}-${whatsapp.slice(9)}`;
    }
    return whatsapp;
}

function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}
