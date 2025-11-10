/**
 * Gerenciamento da aba de Leads
 * Chart.js para gráficos interativos
 */

// API_BASE e API_KEY já declarados no app.js - não redeclarar

let chartScoreInstance = null;
let chartImoveisInstance = null;
let todosLeads = [];
let todosImoveis = [];

// ==================== INICIALIZAÇÃO ====================

document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Leads.js carregado');

    // Tabs navigation
    document.querySelectorAll('.tab-button').forEach(button => {
        button.addEventListener('click', () => {
            const tab = button.dataset.tab;
            console.log('Tab clicada:', tab);
            switchTab(tab);
        });
    });

    // Filtros (somente se elementos existirem)
    const filterScore = document.getElementById('filterScore');
    const filterImovel = document.getElementById('filterImovel');
    const filterAgendamento = document.getElementById('filterAgendamento');
    const btnExportar = document.getElementById('btnExportarLeads');

    if (filterScore) filterScore.addEventListener('change', aplicarFiltros);
    if (filterImovel) filterImovel.addEventListener('change', aplicarFiltros);
    if (filterAgendamento) filterAgendamento.addEventListener('change', aplicarFiltros);
    if (btnExportar) btnExportar.addEventListener('click', exportarLeadsCSV);

    console.log('Event listeners configurados');
});

function switchTab(tabName) {
    console.log('switchTab chamado:', tabName);

    // Atualizar botões
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

    // Atualizar conteúdo
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`tab-${tabName}`).classList.add('active');

    // Carregar dados da aba
    if (tabName === 'leads') {
        console.log('Carregando dados de leads...');
        carregarDadosLeads();
    } else if (tabName === 'agenda') {
        console.log('Aba agenda ativada - carregando dados...');
        if (typeof window.agendaCarregar === 'function') {
            window.agendaCarregar();
        } else {
            console.warn('Função agendaCarregar não encontrada ainda');
        }
    }
}

// ==================== CARREGAR DADOS ====================

async function carregarDadosLeads() {
    console.log('📊 carregarDadosLeads iniciado');

    try {
        console.log('Fazendo requisições paralelas...');

        // Carregar leads, estatísticas e imóveis em paralelo
        const [leadsRes, statsRes, imoveisRes] = await Promise.all([
            fetch(`${API_BASE}/api/leads`, {
                headers: { 'Authorization': `Bearer ${API_KEY}` }
            }),
            fetch(`${API_BASE}/api/estatisticas`, {
                headers: { 'Authorization': `Bearer ${API_KEY}` }
            }),
            fetch(`${API_BASE}/api/imoveis`, {
                headers: { 'Authorization': `Bearer ${API_KEY}` }
            })
        ]);

        console.log('Respostas recebidas:', {
            leads: leadsRes.status,
            stats: statsRes.status,
            imoveis: imoveisRes.status
        });

        const leadsData = await leadsRes.json();
        const statsData = await statsRes.json();
        const imoveisData = await imoveisRes.json();

        console.log('Dados parseados:', {
            totalLeads: leadsData.total,
            totalImoveis: imoveisData.total
        });

        todosLeads = leadsData.leads || [];
        todosImoveis = imoveisData.imoveis || [];

        // Atualizar UI
        console.log('Atualizando UI...');
        atualizarEstatisticas(statsData.estatisticas);
        renderizarGraficos(statsData.estatisticas);
        popularFiltroImoveis(todosImoveis);
        renderizarTabelaLeads(todosLeads);

        console.log('✅ Dados carregados com sucesso');

    } catch (error) {
        console.error('❌ Erro ao carregar dados de leads:', error);
        const leadsBody = document.getElementById('leadsBody');
        if (leadsBody) {
            leadsBody.innerHTML = `
                <tr><td colspan="6" style="color: red; text-align: center;">
                    Erro ao carregar leads: ${error.message}
                </td></tr>
            `;
        }
    }
}

function atualizarEstatisticas(stats) {
    const totalLeads = document.getElementById('totalLeads');
    const scoreMedio = document.getElementById('scoreMedio');
    const totalAgendamentos = document.getElementById('totalAgendamentos');

    if (totalLeads) totalLeads.textContent = stats.total_leads || 0;
    if (scoreMedio) scoreMedio.textContent = stats.score_medio || 0;
    if (totalAgendamentos) totalAgendamentos.textContent = stats.agendamentos?.total_agendamentos || 0;

    console.log('Estatísticas atualizadas:', stats);
}

function popularFiltroImoveis(imoveis) {
    const select = document.getElementById('filterImovel');

    // Limpar opções antigas (manter apenas "Todos")
    select.innerHTML = '<option value="all">Todos os imóveis</option>';

    // Adicionar opções
    imoveis.forEach(imovel => {
        const option = document.createElement('option');
        option.value = imovel.id;
        option.textContent = `${imovel.id} - ${imovel.titulo}`;
        select.appendChild(option);
    });
}

// ==================== GRÁFICOS ====================

function renderizarGraficos(stats) {
    renderizarGraficoScore(stats.distribuicao);
    renderizarGraficoImoveis(stats.por_imovel);
}

function renderizarGraficoScore(distribuicao) {
    const ctx = document.getElementById('chartScore').getContext('2d');

    // Destruir gráfico anterior se existir
    if (chartScoreInstance) {
        chartScoreInstance.destroy();
    }

    chartScoreInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Frios (0-30) ❄️', 'Mornos (31-60) 🌡️', 'Quentes (61-100) 🔥'],
            datasets: [{
                data: [
                    distribuicao?.frios || 0,
                    distribuicao?.mornos || 0,
                    distribuicao?.quentes || 0
                ],
                backgroundColor: [
                    '#60a5fa', // Azul (frio)
                    '#fbbf24', // Amarelo (morno)
                    '#f87171'  // Vermelho (quente)
                ],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 15,
                        font: { size: 12 }
                    }
                }
            }
        }
    });
}

function renderizarGraficoImoveis(porImovel) {
    const ctx = document.getElementById('chartImoveis').getContext('2d');

    // Destruir gráfico anterior se existir
    if (chartImoveisInstance) {
        chartImoveisInstance.destroy();
    }

    // Mapear IDs para títulos
    const labels = porImovel.map(item => {
        const imovel = todosImoveis.find(i => i.id === item.imovel_id);
        return imovel ? imovel.titulo.substring(0, 20) + '...' : `ID ${item.imovel_id}`;
    });

    const data = porImovel.map(item => item.count);

    chartImoveisInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Leads por Imóvel',
                data: data,
                backgroundColor: '#3b82f6',
                borderColor: '#2563eb',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { stepSize: 1 }
                }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}

// ==================== TABELA DE LEADS ====================

function renderizarTabelaLeads(leads) {
    const tbody = document.getElementById('leadsBody');

    if (leads.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align: center;">Nenhum lead encontrado</td></tr>';
        return;
    }

    tbody.innerHTML = leads.map(lead => {
        const scoreClass = getScoreClass(lead.score);
        const scoreEmoji = getScoreEmoji(lead.score);
        const agendouEmoji = lead.agendou_visita ? '✅' : '❌';
        const imovelTitulo = getImovelTitulo(lead.imovel_id);
        const dataAtualizada = formatarData(lead.atualizado_em);

        return `
            <tr>
                <td>${lead.nome}</td>
                <td>${formatarWhatsApp(lead.whatsapp)}</td>
                <td><span class="score-badge ${scoreClass}">${lead.score} ${scoreEmoji}</span></td>
                <td>${imovelTitulo}</td>
                <td style="text-align: center;">${agendouEmoji}</td>
                <td>${dataAtualizada}</td>
                <td>
                    <button onclick="deletarLead('${lead.whatsapp}')" style="background: #ff4444; color: white; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer;">🗑️ Deletar</button>
                </td>
            </tr>
        `;
    }).join('');
}

function getScoreClass(score) {
    if (score >= 61) return 'score-quente';
    if (score >= 31) return 'score-morno';
    return 'score-frio';
}

function getScoreEmoji(score) {
    if (score >= 61) return '🔥';
    if (score >= 31) return '🌡️';
    return '❄️';
}

function getImovelTitulo(imovelId) {
    if (!imovelId) return '-';
    const imovel = todosImoveis.find(i => i.id === imovelId);
    return imovel ? imovel.titulo : `ID ${imovelId}`;
}

function formatarWhatsApp(whatsapp) {
    // Formatar: 55 31 99988-7766
    if (whatsapp.length === 13) {
        return `${whatsapp.substring(0, 2)} ${whatsapp.substring(2, 4)} ${whatsapp.substring(4, 9)}-${whatsapp.substring(9)}`;
    }
    return whatsapp;
}

function formatarData(isoDate) {
    if (!isoDate) return '-';
    const date = new Date(isoDate);
    return date.toLocaleString('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// ==================== FILTROS ====================

function aplicarFiltros() {
    const filterScore = document.getElementById('filterScore').value;
    const filterImovel = document.getElementById('filterImovel').value;
    const filterAgendamento = document.getElementById('filterAgendamento').value;

    let leadsFiltrados = [...todosLeads];

    // Filtro de score
    if (filterScore !== 'all') {
        if (filterScore === 'frio') {
            leadsFiltrados = leadsFiltrados.filter(l => l.score >= 0 && l.score <= 30);
        } else if (filterScore === 'morno') {
            leadsFiltrados = leadsFiltrados.filter(l => l.score >= 31 && l.score <= 60);
        } else if (filterScore === 'quente') {
            leadsFiltrados = leadsFiltrados.filter(l => l.score >= 61 && l.score <= 100);
        }
    }

    // Filtro de imóvel
    if (filterImovel !== 'all') {
        const imovelId = parseInt(filterImovel);
        leadsFiltrados = leadsFiltrados.filter(l => l.imovel_id === imovelId);
    }

    // Filtro de agendamento
    if (filterAgendamento !== 'all') {
        const agendou = filterAgendamento === 'true';
        leadsFiltrados = leadsFiltrados.filter(l => l.agendou_visita === agendou);
    }

    renderizarTabelaLeads(leadsFiltrados);
}

// ==================== EXPORTAR CSV ====================

async function exportarLeadsCSV() {
    const filterScore = document.getElementById('filterScore').value;
    const filterImovel = document.getElementById('filterImovel').value;
    const filterAgendamento = document.getElementById('filterAgendamento').value;

    // Construir query params
    let params = new URLSearchParams();

    if (filterScore === 'frio') {
        params.append('score_min', '0');
        params.append('score_max', '30');
    } else if (filterScore === 'morno') {
        params.append('score_min', '31');
        params.append('score_max', '60');
    } else if (filterScore === 'quente') {
        params.append('score_min', '61');
        params.append('score_max', '100');
    }

    if (filterImovel !== 'all') {
        params.append('imovel_id', filterImovel);
    }

    if (filterAgendamento !== 'all') {
        params.append('agendou_visita', filterAgendamento);
    }

    try {
        const response = await fetch(`${API_BASE}/api/leads/export?${params.toString()}`, {
            headers: { 'Authorization': `Bearer ${API_KEY}` }
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `leads_${new Date().toISOString().split('T')[0]}.csv`;
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);
        } else {
            alert('Erro ao exportar CSV');
        }
    } catch (error) {
        console.error('Erro ao exportar:', error);
        alert('Erro ao exportar CSV');
    }
}

// ==================== DELETAR LEAD ====================

async function deletarLead(whatsapp) {
    try {
        const response = await fetch(`${API_BASE}/api/leads/${whatsapp}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${API_KEY}` }
        });

        const result = await response.json();

        if (result.success) {
            // Recarregar dados automaticamente
            carregarDadosLeads();
        } else {
            alert('❌ Erro: ' + result.error);
        }
    } catch (error) {
        console.error('Erro ao deletar lead:', error);
        alert('Erro ao deletar lead: ' + error.message);
    }
}

window.deletarLead = deletarLead;
