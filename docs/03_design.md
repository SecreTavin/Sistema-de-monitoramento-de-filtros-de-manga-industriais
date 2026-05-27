# Design System & UI/UX Specifications
## Tema: Glassmorphism & Transições Fluidas (GSAP)

Este documento define as regras visuais e o sistema de design que guiarão a implementação frontend solicitada no PRD (docs/01_prd.md).

### 1. Paleta de Cores
Para que o efeito "Glassmorphism" (Translúcido) funcione corretamente, precisamos de um fundo vibrante ou escuro com contraste, e elementos translúcidos por cima.

*   **Fundo Principal (Background):** Gradiente Mesh ou Gradiente linear dinâmico.
    *   CSS: `background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);`
*   **Containers Translúcidos (Glass Base):**
    *   Fundo: Branco com baixa opacidade `rgba(255, 255, 255, 0.05)` a `rgba(255, 255, 255, 0.1)`
    *   Bordas: Brancas e sutis `rgba(255, 255, 255, 0.18)`
    *   Sombras: Sombras escuras e difusas para criar profundidade `rgba(0, 0, 0, 0.25)`
*   **Tipografia (Texto sobre o Glass):**
    *   Primária (Títulos): Branco Puro `#FFFFFF`
    *   Secundária (Corpo/Filtros): Cinza Claro `#E2E8F0`
    *   Destaques (Hover/Ativo): Azul Cian `#38BDF8`

### 2. Tipografia
*   **Fonte Principal:** `Inter`, `Roboto` ou `system-ui` (fontes sem serifa, limpas e modernas).
*   **Tamanhos:**
    *   H1/Títulos de Seção: `2.25rem` (36px), *Semibold*
    *   Filtros/Labels: `1rem` (16px), *Medium*
    *   Texto de Apoio: `0.875rem` (14px), *Regular*

### 3. Tokens do Tailwind CSS (Glassmorphism)
Caso o desenvolvimento utilize Tailwind CSS (fortemente recomendado para este design), os componentes translúcidos devem utilizar a seguinte combinação de classes base:

```html
<!-- Componente Base Glassmorphism -->
<div class="bg-white/10 backdrop-blur-md border border-white/20 shadow-xl rounded-2xl">
    <!-- Conteúdo -->
</div>
```
*   `bg-white/10`: Fundo translúcido.
*   `backdrop-blur-md`: O desfoque fundamental para o efeito de vidro fosco.
*   `border-white/20`: Borda suave para simular o reflexo da borda do vidro.
*   `shadow-xl`: Sombra para flutuação.
*   `rounded-2xl`: Cantos arredondados amigáveis (1rem / 16px).

### 4. Especificações de Animação (GSAP)
O GSAP será utilizado para injetar vida à interface, seguindo a diretriz do PRD. As curvas de animação devem ser suaves (premium feel).

*   **Curva Padrão (Easing):** `power3.out` (Rápido no início, suaviza no final).
*   **Tempos (Durations):**
    *   Micro-interações (Hover de botões/filtros): `0.3s`
    *   Entrada de Elementos (Fade/Slide in): `0.6s`
    *   Transições de Lista/Filtragem: `0.4s` com `stagger: 0.05s` (Efeito em cascata).
*   **Comportamento de Seleção/Hover (Itens da Lista):**
    *   Ação: Subir levemente o eixo Y e aumentar escala.
    *   GSAP: `gsap.to(item, { y: -5, scale: 1.02, duration: 0.3, ease: "power2.out" })`
*   **Acessibilidade (Reduced Motion):**
    *   A lógica de inicialização do GSAP deve ser desativada se `window.matchMedia('(prefers-reduced-motion: reduce)').matches` for verdadeiro.