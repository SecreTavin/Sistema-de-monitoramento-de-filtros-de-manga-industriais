Sistema de monitoramento de filtros de manga industriais

(Sistema não finalizado, ainda em andamento).
Este projeto consiste em um sistema para monitorar filtros de manga industriais, onde o sistema permite o acompanhamento em tempo real da perda de pressão
(deltaP) automatizando a análise da integridade dos elementos filtrantes e otimizando o cronograma de manutenção.

Funcionalidades:
- Gestão de ativos(CRUD): Cadastro e edição de filtros com especificações técnicas (id, quantidade de mangas, material, pressão.)
- Monitoramento em tempo real: Dashboard interativo que consome uma API para verificar os status operacional baseado na pressão diferencial (DeltaP).
- Lógica de status automática:
  .Operacional: pressão dentro dos parâmetros de execução.
  .Atenção: Alerta de ínicio de comitação ou saturação.
  .Crítico: Necessidade de intervenção imediata ou substituição dos elementos filtrantes.
_ Inventário: Tabela consolidada de todos os ativos cadastrados com indicadores visuais de status.
_ Histórico de manutenção: Controle de datas para cumprimento de cronogramas de inspeção.

Tecnologias utilizadas:
- Backend: python 3.12 com flask (API rest).
- Persistência de dados: MySQL integrado via SQLAlchemy(ORM).
- Frontend: HTML5, CSS3 e JavaScript(Fetch API).

Estrutura do projeto:

PROJETO-FILTRO/
├── project/
│   ├── monitoramento.py    # Servidor Flask e Lógica de Banco de Dados
│   ├── templates/          # Arquivos HTML (Frontend)
│   └── static/             # Estilização CSS e Ativos Visuais

Desenvolvido por Octavio Augusto Arruda dos Prazeres, estudante de engenharia de software. Este projeto une conhecimentos em mecânica industrial e desenvolvimento de sistemas.
