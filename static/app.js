// Configurações
const API_BASE = '';
const API_KEY = 'dev-token-12345'; // Mesmo token do servidor

// Estado da aplicação
let imoveis = [];
let imovelEditando = null;

// Elementos DOM
const imoveisBody = document.getElementById('imoveisBody');
const modalImovel = document.getElementById('modalImovel');
const formImovel = document.getElementById('formImovel');
const btnNovoImovel = document.getElementById('btnNovoImovel');
const btnFecharModal = document.getElementById('btnFecharModal');
const btnCancelar = document.getElementById('btnCancelar');
const modalTitle = document.getElementById('modalTitle');
const searchInput = document.getElementById('searchInput');
const btnAdicionarFoto = document.getElementById('btnAdicionarFoto');
const fotosContainer = document.getElementById('fotosContainer');

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
    carregarImoveis();
    setupEventListeners();
});

// Setup de eventos
function setupEventListeners() {
    btnNovoImovel.addEventListener('click', abrirModalNovo);
    btnFecharModal.addEventListener('click', fecharModal);
    btnCancelar.addEventListener('click', fecharModal);
    formImovel.addEventListener('submit', salvarImovel);
    searchInput.addEventListener('input', filtrarImoveis);
    btnAdicionarFoto.addEventListener('click', adicionarCampoFoto);

    // Fechar modal ao clicar fora
    modalImovel.addEventListener('click', (e) => {
        if (e.target === modalImovel) {
            fecharModal();
        }
    });
}

// Carregar imóveis
async function carregarImoveis() {
    try {
        imoveisBody.innerHTML = '<tr><td colspan="8" class="loading">Carregando imóveis...</td></tr>';

        const response = await fetch(`${API_BASE}/api/imoveis`, {
            headers: {
                'Authorization': `Bearer ${API_KEY}`
            }
        });

        if (!response.ok) {
            throw new Error('Erro ao carregar imóveis');
        }

        const data = await response.json();
        imoveis = data.imoveis;

        renderizarImoveis(imoveis);
        atualizarStats();
    } catch (error) {
        console.error('Erro:', error);
        imoveisBody.innerHTML = `<tr><td colspan="8" class="empty">❌ Erro ao carregar imóveis: ${error.message}</td></tr>`;
    }
}

// Renderizar tabela de imóveis
function renderizarImoveis(lista) {
    if (lista.length === 0) {
        imoveisBody.innerHTML = '<tr><td colspan="8" class="empty">Nenhum imóvel cadastrado. Clique em "+ Novo Imóvel" para começar.</td></tr>';
        return;
    }

    imoveisBody.innerHTML = lista.map(imovel => `
        <tr>
            <td>${imovel.id}</td>
            <td>${imovel.titulo}</td>
            <td>${capitalize(imovel.tipo)}</td>
            <td>${imovel.cidade}</td>
            <td>${imovel.area_m2 || '-'}</td>
            <td>${formatarPreco(imovel.preco_total_min)}</td>
            <td><span class="status-badge status-${imovel.status}">${capitalize(imovel.status)}</span></td>
            <td>
                <div class="action-buttons">
                    <button class="btn btn-primary btn-small" onclick="editarImovel(${imovel.id})">✏️ Editar</button>
                    <button class="btn btn-danger btn-small" onclick="confirmarDeletar(${imovel.id})">🗑️ Deletar</button>
                </div>
            </td>
        </tr>
    `).join('');
}

// Atualizar estatísticas
function atualizarStats() {
    document.getElementById('totalImoveis').textContent = imoveis.length;
    document.getElementById('disponiveis').textContent = imoveis.filter(i => i.status === 'disponivel').length;
}

// Filtrar imóveis
function filtrarImoveis() {
    const termo = searchInput.value.toLowerCase();
    const imoveisFiltrados = imoveis.filter(imovel =>
        imovel.titulo.toLowerCase().includes(termo) ||
        imovel.cidade.toLowerCase().includes(termo) ||
        imovel.tipo.toLowerCase().includes(termo)
    );
    renderizarImoveis(imoveisFiltrados);
}

// Abrir modal para novo imóvel
function abrirModalNovo() {
    imovelEditando = null;
    modalTitle.textContent = 'Novo Imóvel';
    formImovel.reset();
    resetarCamposFotos();
    modalImovel.classList.add('active');
}

// Abrir modal para editar
async function editarImovel(id) {
    try {
        // Buscar dados completos do imóvel
        const [imovelRes, faqRes, fotosRes] = await Promise.all([
            fetch(`${API_BASE}/api/imoveis/${id}`, {
                headers: { 'Authorization': `Bearer ${API_KEY}` }
            }),
            fetch(`${API_BASE}/api/imoveis/${id}/faq`, {
                headers: { 'Authorization': `Bearer ${API_KEY}` }
            }),
            fetch(`${API_BASE}/api/imoveis/${id}/fotos`, {
                headers: { 'Authorization': `Bearer ${API_KEY}` }
            })
        ]);

        const imovelData = await imovelRes.json();
        const faqData = await faqRes.json();
        const fotosData = await fotosRes.json();

        imovelEditando = imovelData.imovel;

        // Preencher formulário
        document.getElementById('titulo').value = imovelEditando.titulo;
        document.getElementById('tipo').value = imovelEditando.tipo;
        document.getElementById('cidade').value = imovelEditando.cidade;
        document.getElementById('area_m2').value = imovelEditando.area_m2 || '';
        document.getElementById('preco_total_min').value = imovelEditando.preco_total_min || '';
        document.getElementById('status').value = imovelEditando.status;
        document.getElementById('faq').value = faqData.faq || '';
        document.getElementById('video_tour').value = fotosData.video_tour || '';
        document.getElementById('planta_baixa').value = fotosData.planta_baixa || '';

        // Preencher fotos
        resetarCamposFotos();
        if (fotosData.fotos && fotosData.fotos.length > 0) {
            fotosData.fotos.forEach((url, index) => {
                if (index === 0) {
                    fotosContainer.querySelector('.foto-url').value = url;
                } else {
                    adicionarCampoFoto(url);
                }
            });
        }

        modalTitle.textContent = 'Editar Imóvel';
        modalImovel.classList.add('active');
    } catch (error) {
        console.error('Erro ao carregar imóvel:', error);
        alert('Erro ao carregar dados do imóvel');
    }
}

// Fechar modal
function fecharModal() {
    modalImovel.classList.remove('active');
    formImovel.reset();
    imovelEditando = null;
}

// Salvar imóvel
async function salvarImovel(e) {
    e.preventDefault();

    const formData = new FormData(formImovel);
    const dados = {
        titulo: formData.get('titulo'),
        tipo: formData.get('tipo'),
        cidade: formData.get('cidade'),
        area_m2: parseInt(formData.get('area_m2')) || 0,
        preco_total_min: parseInt(formData.get('preco_total_min')) || 0,
        status: formData.get('status'),
        faq: formData.get('faq'),
        video_tour: formData.get('video_tour') || null,
        planta_baixa: formData.get('planta_baixa') || null,
        fotos: []
    };

    // Coletar URLs das fotos
    document.querySelectorAll('.foto-url').forEach(input => {
        if (input.value.trim()) {
            dados.fotos.push(input.value.trim());
        }
    });

    try {
        let response;
        if (imovelEditando) {
            // Atualizar
            response = await fetch(`${API_BASE}/api/imoveis/${imovelEditando.id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(dados)
            });
        } else {
            // Criar
            response = await fetch(`${API_BASE}/api/imoveis`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(dados)
            });
        }

        if (!response.ok) {
            throw new Error('Erro ao salvar imóvel');
        }

        const result = await response.json();
        console.log('Sucesso:', result);

        fecharModal();
        carregarImoveis();

        alert(imovelEditando ? 'Imóvel atualizado com sucesso!' : 'Imóvel criado com sucesso!');
    } catch (error) {
        console.error('Erro:', error);
        alert(`Erro ao salvar imóvel: ${error.message}`);
    }
}

// Confirmar deleção
async function confirmarDeletar(id) {
    const imovel = imoveis.find(i => i.id === id);
    if (!confirm(`Tem certeza que deseja deletar "${imovel.titulo}"?`)) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/api/imoveis/${id}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            throw new Error('Erro ao deletar imóvel');
        }

        alert('Imóvel deletado com sucesso!');
        carregarImoveis();
    } catch (error) {
        console.error('Erro:', error);
        alert(`Erro ao deletar imóvel: ${error.message}`);
    }
}

// Adicionar campo de foto
function adicionarCampoFoto(url = '') {
    const div = document.createElement('div');
    div.className = 'foto-input';
    div.innerHTML = `
        <input type="url" class="foto-url" placeholder="https://exemplo.com/foto.jpg" value="${url}">
        <button type="button" class="btn-remove-foto" onclick="removerCampoFoto(this)">✕</button>
    `;
    fotosContainer.appendChild(div);
}

// Remover campo de foto
function removerCampoFoto(btn) {
    btn.parentElement.remove();
}

// Resetar campos de fotos
function resetarCamposFotos() {
    fotosContainer.innerHTML = `
        <div class="foto-input">
            <input type="url" class="foto-url" placeholder="https://exemplo.com/foto1.jpg">
            <button type="button" class="btn-remove-foto" style="display:none;">✕</button>
        </div>
    `;
}

// Helpers
function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

function formatarPreco(valor) {
    if (!valor) return '-';
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL',
        minimumFractionDigits: 0
    }).format(valor);
}
