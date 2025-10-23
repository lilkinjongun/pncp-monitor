# Frontend - Dashboard PNCP

Dashboard web interativo para visualização das contratações públicas monitoradas.

## 🎨 Tecnologias

- **React** com TypeScript
- **Wouter** para roteamento
- **Shadcn/ui** para componentes
- **Tailwind CSS** para estilização
- **Lucide React** para ícones

## 📁 Estrutura

```
frontend/
├── src/
│   ├── App.tsx                    # Componente principal e roteamento
│   ├── index.css                  # Estilos globais
│   ├── pages/
│   │   ├── Home.tsx              # Página inicial com estatísticas
│   │   ├── Contratacoes.tsx      # Lista de contratações
│   │   └── Estatisticas.tsx      # Gráficos e análises
│   └── components/
│       └── DashboardLayout.tsx   # Layout com sidebar
```

## 🚀 Como Usar

### Pré-requisitos

- Node.js 18+
- pnpm (ou npm/yarn)

### Instalação

```bash
cd frontend
pnpm install
```

### Desenvolvimento

```bash
pnpm dev
```

O dashboard estará disponível em `http://localhost:5173`

### Build para Produção

```bash
pnpm build
```

## 🔌 Integração com Backend

O frontend está preparado para consumir dados de uma API REST. Atualmente, os dados são mockados, mas você pode integrar com o backend Python:

1. **Criar API REST** usando Flask ou FastAPI
2. **Expor endpoints**:
   - `GET /api/stats` - Estatísticas gerais
   - `GET /api/contratacoes` - Lista de contratações
   - `GET /api/estatisticas` - Dados para gráficos

3. **Atualizar os componentes** para fazer requisições HTTP aos endpoints

### Exemplo de Integração

```typescript
// Em Home.tsx
useEffect(() => {
  fetch('/api/stats')
    .then(res => res.json())
    .then(data => setStats(data))
    .catch(err => console.error(err));
}, []);
```

## 🎨 Funcionalidades

### Página Inicial (Home)
- Cards com estatísticas principais
- Total de contratações
- Valor total estimado
- Data da última atualização
- Contratações recentes (30 dias)

### Página de Contratações
- Tabela completa com todas as contratações
- Filtros e ordenação
- Links diretos para o PNCP
- Badges coloridos por modalidade

### Página de Estatísticas
- Gráficos de análise
- Distribuição por modalidade
- Evolução temporal
- Análise de valores

## 🎯 Próximas Melhorias

- [ ] Integração real com API backend
- [ ] Filtros avançados na tabela
- [ ] Exportação de dados (CSV, PDF)
- [ ] Gráficos interativos (Chart.js ou Recharts)
- [ ] Sistema de busca
- [ ] Paginação da tabela
- [ ] Modo claro/escuro toggle

## 📝 Notas

- O tema padrão é **escuro** (configurado no ThemeProvider)
- Os componentes UI são do **shadcn/ui**
- O design é **responsivo** e funciona em mobile

