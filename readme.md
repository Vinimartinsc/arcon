# ARCON – Ferramenta de Conversão de Acervos

_This document is available in [English](./docs/readme.en.md)._

## Sumário

- O que é o ARCON?
- Principais Funcionalidades
- Sobre o Projeto
- Primeiros Passos

## O que é o ARCON?

O ARCON é uma ferramenta **open-source**, independente de plataforma, voltada ao processamento de imagens e projetada para apoiar fluxos de trabalho de digitalização arquivística, combinando conversão de formato de imagem e incorporação de metadados em um único processo.

## Principais Funcionalidades

- Preservação da estrutura hierárquica original de pastas  
- Conversão em lote de imagens RAW para JPEG  
- Incorporação de metadados de licenciamento e autoria  
- Inclusão de metadados para desencorajar o uso por sistemas de IA  
- Interface baseada em navegador e modo de linha de comando (CLI)  

## Sobre o Projeto

Ao digitalizar um acervo físico, é fundamental preservar um gêmeo digital de alta qualidade, o mais fiel possível ao material original. Muitas câmeras digitais capturam imagens em formatos RAW, também conhecidos como “Negativos Digitais”. Isso ocorre porque o formato RAW retém uma grande quantidade de informações do sensor da câmera, incluindo metadados técnicos detalhados.

Por esse motivo, arquivos RAW podem ser utilizados em processos profissionais de digitalização arquivística e podem ser considerados adequados para fins forenses e probatórios.

No entanto, os formatos RAW não são apropriados para a disseminação pública. A maioria das plataformas web e redes sociais não oferece suporte nativo a esses formatos, o que limita o acesso e o reuso do conteúdo. Assim, acervos destinados ao acesso online normalmente exigem a conversão para formatos amplamente aceitos, como o JPEG.

Paralelamente, a publicação de acervos digitalizados levanta preocupações relacionadas a licenciamento, autoria, direitos autorais e uso adequado, especialmente no contexto dos avanços recentes em sistemas de inteligência artificial generativa.

O ARCON integra a conversão de formatos de imagem e a incorporação de metadados justamente para atender a esse propósito.

## Primeiros Passos

### Instalação

```sh
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Build

```sh
pyinstaller arcon.spec
```

## Uso

```sh
./arcon
```

### CLI

```sh
./arcon -- -h
```
