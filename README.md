# 🎯 Desafio ENEM — Banco de Questões 2009–2023

> Banco de dados com **1.868 questões oficiais do ENEM** (2009 a 2023), organizadas por ano, disciplina e questão — pronto para alimentar apps de simulado e estudo.

## 📌 Sobre

Este repositório contém um acervo estruturado de questões do **Exame Nacional do Ensino Médio (ENEM)**, incluindo:

- ✅ **15 anos de provas** (2009 → 2023)
- ✅ **1.868 questões** com enunciado completo
- ✅ **Gabarito oficial** (alternativa correta) em cada questão
- ✅ **Disciplinas** classificadas (Ciências Humanas, Ciências da Natureza, Linguagens, Matemática)
- ✅ **Imagens** dos enunciados quando necessário
- ✅ Dados em **JSON estruturado** — fácil de consumir em qualquer aplicação

## 📁 Estrutura

```
public/
├── exams.json                 # Índice geral dos exames por ano
├── <ano>/                     # Ex.: 2009, 2010, ..., 2023
│   ├── details.json           # Metadados do exame (disciplinas)
│   └── questions/
│       ├── <id>/
│       │   ├── details.json   # Questão completa (enunciado, alternativas, gabarito)
│       │   └── <imagem>.jpg   # Imagens do enunciado (quando houver)
│       └── ...
└── broken-image.svg           # Fallback para imagens ausentes
```

### Exemplo de questão (`details.json`)

```json
{
  "title": "Questão 1 - ENEM 2010",
  "index": 1,
  "year": 2010,
  "discipline": "ciencias-humanas",
  "context": "O gráfico representa a relação entre...",
  "correctAlternative": "A",
  "alternatives": { "A": "...", "B": "...", "C": "...", "D": "...", "E": "..." }
}
```

## 🚀 Como usar

O banco é **100% estático** — funciona em qualquer linguagem/framework:

```js
// Exemplo (JS/TS)
const questoes = await fetch('/public/exams.json').then(r => r.json());
const prova2019 = await fetch('/public/2019/details.json').then(r => r.json());
```

Ou sirva a pasta `public/` com qualquer servidor estático:

```bash
python -m http.server 8000
# ou
npx serve public
```

## 🛠️ Ideias de uso

- 🧪 App de **simulado** com cronômetro e correção automática
- 📱 App de **estudo por disciplina** (filtro por matéria)
- 🔁 Gerador de **revisão espaçada** (flashcards de questões erradas)
- 📊 Análise de **temas mais cobrados** por ano

## ⚖️ Sobre as questões

As questões são de **provas públicas do ENEM** (INEP/MEC) — material de domínio público para fins educacionais. Este repositório é um projeto **independente e sem fins lucrativos**, não afiliado ao INEP.

## 👤 Autor

**Alexandre Ramos** — [github.com/Alexsantossp71](https://github.com/Alexsantossp71)

## 📄 Status

Em desenvolvimento — novas provas são adicionadas conforme disponibilidade.
