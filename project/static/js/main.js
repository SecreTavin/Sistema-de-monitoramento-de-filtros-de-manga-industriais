async function chamarPython() {
            const id = document.getElementById('idFiltro').value;
            const campoResultado = document.getElementById('resultado');
            if (!id) return;

            try {
                const resposta = await fetch(`/api/analisar/${id}`);
                const dados = await resposta.json();

                if (dados.erro || !resposta.ok) {
                    campoResultado.innerHTML = `<p style="color: var(--status-crit);">⚠️ ${dados.erro || dados.mensagem}</p>`;
                    campoResultado.style.borderColor = 'var(--status-crit)';
                    
                    if (typeof gsap !== "undefined" && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
                        gsap.from(campoResultado.querySelector('p'), { duration: 0.3, x: -10, opacity: 0, ease: "power2.out" });
                    }
                } else {
                    let corStatus = 'var(--status-ok)';
                    if (dados.status === 'CRÍTICO') corStatus = 'var(--status-crit)';
                    if (dados.status === 'ATENÇÃO') corStatus = 'var(--status-warn)';

                    campoResultado.innerHTML = `
                        <h3 style="margin-bottom: 10px; color: white;">Ativo ID: ${dados.id}</h3>
                        <div style="margin-bottom: 10px;">
                            <span class="status-badge" style="background-color: ${corStatus}; color: ${dados.status === 'ATENÇÃO' ? '#000' : '#fff'};">
                                ${dados.status}
                            </span>
                        </div>
                        <div class="resultado-grid">
                            <div class="resultado-dado">
                                <small style="color: var(--text-muted);">Pressão Delta P</small>
                                <p style="font-size: 1.2rem; font-weight: bold;">${dados.deltap} mmH2O</p>
                            </div>
                            <div class="resultado-dado">
                                <small style="color: var(--text-muted);">Mensagem do Sistema</small>
                                <p style="font-size: 0.9rem;">${dados.mensagem.split(',')[0]}</p>
                            </div>
                            <div class="resultado-avaria">
                                <small style="color: var(--text-muted);">📋 Último Relatório de Avarias</small>
                                <p style="margin-top: 5px; line-height: 1.4;">${dados.observacoes || "Nenhuma avaria registrada."}</p>
                            </div>
                        </div>
                    `;
                    campoResultado.style.borderColor = corStatus;

                    // Animação de entrada dos dados retornados pelo backend no Diagnóstico (GSAP)
                    if (typeof gsap !== "undefined" && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
                        // Animação do cabeçalho (ID e Badge)
                        gsap.from("#resultado h3, #resultado .status-badge", {
                            duration: 0.4, y: -10, opacity: 0, stagger: 0.1, ease: "power2.out"
                        });
                        // Animação em cascata dos cards de informação da telemetria
                        gsap.from("#resultado .resultado-dado, #resultado .resultado-avaria", {
                            duration: 0.5, y: 15, opacity: 0, stagger: 0.1, delay: 0.15, ease: "power3.out"
                        });
                    }
                }
            } catch (erro) { console.error("Erro:", erro); }
        }

        async function cadastrarFiltro() {
            const id = document.getElementById('cadId').value;
            if(!id) { alert("O ID é obrigatório!"); return; }

            const dados = {
                id: id,
                quantidade_mangas: document.getElementById('cadMangas').value || 0,
                material_manga: document.getElementById('cadMaterial').value || 'Não especificado'
            };

            const resposta = await fetch('/api/cadastrar', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(dados)
            });
            const result = await resposta.json();
            alert(result.mensagem || result.erro);
            carregarInventario();
        }

        async function atualizarDados() {
            const id = document.getElementById('updId').value;
            if(!id) { alert("Informe o ID do filtro para registrar a inspeção."); return; }

            const dados = {
                id: id, deltap: document.getElementById('updDeltap').value,
                manutencao: document.getElementById('updData').value,
                observacoes: document.getElementById('updObservacoes').value 
            };

            const resposta = await fetch('/api/atualizar', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(dados)
            });
            const result = await resposta.json();
            alert(result.mensagem || result.erro);
            
            document.getElementById('updObservacoes').value = ''; 
            document.getElementById('updDeltap').value = '';
            
            if(document.getElementById('idFiltro').value == id) chamarPython(); 
            carregarInventario();
        }

        
        async function excluirFiltro(id) {
            const confirmacao = confirm(`⚠️ ATENÇÃO: Tem certeza que deseja excluir o ativo ${id} definitivamente do sistema?`);
            if (!confirmacao) return; 

            try {
                const resposta = await fetch(`/api/excluir/${id}`, { method: 'DELETE' });
                const result = await resposta.json();
                alert(result.mensagem || result.erro);
                
                carregarInventario();
                if (document.getElementById('idFiltro').value == id) {
                    document.getElementById('resultado').innerHTML = '<p style="color: var(--text-muted); text-align: center;">Insira um ID e clique em analisar.</p>';
                    document.getElementById('resultado').style.borderColor = 'var(--border-color)';
                }
            } catch (erro) {
                console.error("Erro ao excluir:", erro);
                alert("Erro de conexão ao tentar excluir o ativo.");
            }
        }

        async function carregarInventario() {
            const container = document.getElementById('tabelaInventario');
            
            try {
                const resposta = await fetch('/api/historico/');
                const filtros = await resposta.json();

                if (filtros.length === 0) {
                    container.innerHTML = "<p style='text-align:center;'>Nenhum ativo localizado no banco de dados.</p>";
                    return;
                }

                let html = `
                    <table>
                        <thead>
                            <tr>
                                <th>TAG / ID</th>
                                <th>Status Atual</th>
                                <th>Pressão (mmH2O)</th>
                                <th>Última Manutenção</th>
                                <th>Relatório de Avarias</th>
                                <th>Ações</th> 
                            </tr>
                        </thead>
                        <tbody>`;

                filtros.forEach(f => {
                    let corFundo = 'var(--status-ok)'; let corTexto = 'white';
                    if (f.status === 'CRÍTICO') { corFundo = 'var(--status-crit)'; } 
                    else if (f.status === 'ATENÇÃO') { corFundo = 'var(--status-warn)'; corTexto = 'black'; }

                    let obs = f.observacoes ? f.observacoes : '-';

                    html += `
                        <tr>
                            <td style="font-weight: bold;">${f.id}</td>
                            <td><span class="status-badge" style="background-color: ${corFundo}; color: ${corTexto};">${f.status}</span></td>
                            <td>${f.deltap}</td>
                            <td>${f.ultima_manutencao}</td>
                            <td><div class="obs-cell" title="${obs}">${obs}</div></td>
                            <td>
                                <button class="btn-danger" onclick="excluirFiltro(${f.id})" title="Excluir Ativo">␡</button>
                            </td>
                        </tr>`;
                });

                html += '</tbody></table>';
                container.innerHTML = html;

                // Animação de entrada dos itens da tabela com GSAP e Efeitos de Hover
                if (typeof gsap !== "undefined" && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
                    const linhas = container.querySelectorAll("tbody tr");
                    gsap.from(linhas, {
                        duration: 0.4,
                        y: 15,
                        opacity: 0,
                        stagger: 0.05,
                        ease: "power2.out"
                    });

                    // Micro-interações de Hover nas linhas
                    linhas.forEach(linha => {
                        linha.addEventListener("mouseenter", () => {
                            gsap.to(linha, { y: -2, scale: 1.01, backgroundColor: "rgba(255, 255, 255, 0.08)", duration: 0.2, ease: "power2.out" });
                        });
                        linha.addEventListener("mouseleave", () => {
                            gsap.to(linha, { y: 0, scale: 1, backgroundColor: "transparent", duration: 0.2, ease: "power2.out" });
                        });
                    });
                }

            } catch (erro) {
                console.error("Erro ao carregar inventário:", erro);
                container.innerHTML = "<p style='color: var(--status-crit);'>Erro de conexão com o servidor.</p>";
            }
        }

        async function fazerLogout() {
            await fetch('/api/logout', { method: 'POST' });
            window.location.href = "/login";
}

        window.onload = () => {
            carregarInventario();
            setInterval(carregarInventario, 10000); 

            // Animação de entrada dos cards com GSAP
            if (typeof gsap !== "undefined" && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
                gsap.from(".card-industrial", {
                    duration: 0.6,
                    y: 40,
                    opacity: 0,
                    stagger: 0.1,
                    ease: "power3.out"
                });
            }
        };