# Sistema de Gestão de Supermercado

Sistema completo para gestão de supermercado com PDV, controle de estoque, promoções automáticas e integração com hardware.

## 🚀 Funcionalidades

- **PDV Completo**: Vendas com código de barras, balança e impressora
- **Controle de Estoque**: Gestão completa com alertas automáticos
- **Promoções Inteligentes**: Descontos automáticos por quantidade
- **Relatórios Gerenciais**: Dashboard e relatórios detalhados
- **Gestão de Clientes**: Programa de fidelidade e histórico
- **Multi-usuário**: Diferentes níveis de acesso

## 🛠️ Tecnologias

- **Backend**: Python + FastAPI
- **Banco de Dados**: PostgreSQL / SQLite
- **Frontend**: Streamlit
- **Hardware**: Integração com leitor, balança, impressora
- **Deploy**: Docker + Docker Compose

## 📋 Pré-requisitos

- Python 3.11+
- PostgreSQL (opcional, usa SQLite por padrão)
- Docker e Docker Compose (opcional)

## 🚀 Instalação

### Opção 1: Instalação Local

```bash
# Clonar o repositório
git clone <seu-repositorio>
cd supermarket-system

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com suas configurações

# Executar migrações
alembic upgrade head

# Iniciar servidor
uvicorn app.main:app --reload
```

### Opção 2: Docker

```bash
# Subir todos os serviços
cd docker
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar serviços
docker-compose down
```

## 📱 Acesso

- **API**: http://localhost:8000
- **Documentação**: http://localhost:8000/docs
- **Interface Admin**: http://localhost:8501

## 🔧 Configuração de Hardware

### Leitor de Código de Barras
```env
BARCODE_READER_ENABLED=true
BARCODE_READER_PORT=auto  # ou COM1, /dev/ttyUSB0
```

### Balança Eletrônica
```env
SCALE_ENABLED=true
SCALE_PORT=COM1
SCALE_BAUDRATE=9600
```

### Impressora Térmica
```env
PRINTER_ENABLED=true
PRINTER_PORT=COM2
```

## 📖 Documentação

- [Guia de Instalação](docs/installation.md)
- [Configuração de Hardware](docs/hardware.md)
- [Manual do Usuário](docs/user-guide.md)
- [API Reference](docs/api.md)

## 🧪 Testes

```bash
# Executar todos os testes
pytest

# Executar testes com cobertura
pytest --cov=app tests/

# Executar testes específicos
pytest tests/unit/
pytest tests/integration/
```

## 📊 Estrutura do Projeto

```
supermarket-system/
├── app/                    # Código da aplicação
│   ├── core/              # Configurações e segurança
│   ├── domain/            # Entidades e regras de negócio
│   ├── application/       # Casos de uso e serviços
│   ├── infrastructure/    # Banco, hardware, repositórios
│   ├── presentation/      # API e schemas
│   └── ui/               # Interface Streamlit
├── tests/                 # Testes automatizados
├── migrations/            # Migrações do banco
├── docker/               # Configurações Docker
├── docs/                 # Documentação
└── scripts/              # Scripts utilitários
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie sua feature branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🆘 Suporte

- **Documentação**: Consulte a pasta `docs/`
- **Issues**: Abra uma issue no GitHub
- **Email**: seu.email@exemplo.com

## 📈 Roadmap

- [ ] Módulo de compras avançado
- [ ] Integração com NFe
- [ ] App mobile para inventário
- [ ] Relatórios avançados com BI
- [ ] Integração com marketplace

---

**Desenvolvido com ❤️ para modernizar seu supermercado**
