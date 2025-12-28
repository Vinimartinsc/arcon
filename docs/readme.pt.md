# ARCON – Ferramenta de Conversão de Acervos

_This documentation is also available in [English](../readme.md)._

_to build this project refer to [Build](./BUILD.md)

Ao digitalizar um acervo físico, é fundamental preservar um gêmeo digital de alta qualidade, comparável ao material original. Algumas câmeras digitais capturam imagens em formatos RAW, que preservam o máximo de informações registradas pelo sensor da câmera, incluindo metadados técnicos detalhados. Por esse motivo, arquivos RAW podem ser utilizados em acervos digitais e são frequentemente considerados adequados para perícias forenses.

No entanto, formatos RAW não são apropriados para distribuição pública, pois a maioria das plataformas online e redes sociais não oferece suporte nativo a esses formatos. Isso torna necessária a conversão para outros formatos amplamente aceitos na internet, a fim de facilitar o acesso e a difusão do conteúdo.

Com a difusão do acervo digitalizado, emergem preocupações relacionadas a licenciamento, autoria, direitos autorais e uso adequado do conteúdo, especialmente diante do avanço das tecnologias de inteligência artificial generativa, que possibilitam a criação de versões que modificam o conteúdo original dos documentos. Uma estratégia para mitigar o uso indevido, incluindo o uso por crawlers e sistemas de IA, do acervo distribuído na internet é a incorporação de metadados de licenciamento, titularidade e restrições de uso por IA e robôs diretamente nos arquivos de imagem.

## O que é o ARCON?

O **ARCON** é uma ferramenta de conversão de acervos, independente de plataforma, projetada para apoiar fluxos de trabalho de digitalização arquivística, combinando conversão de formato e aplicação de metadados em um único processo.

O ARCON foi desenvolvido para:
 
- Preservar a estrutura hierárquica original do acervo digitalizado  
- Converter imagens em lote para um formato de saída definido  
- Incorporar metadados de licenciamento, autoria e direitos autorais diretamente nos arquivos convertidos  
- Adicionar metadados voltados à limitação do uso do conteúdo por sistemas de IA  

## Por que não utilizar ferramentas de conversão existentes?

A maioria das ferramentas de conversão em lote disponíveis:

- Não é projetada para fluxos de trabalho arquivísticos  
- Não preserva a estrutura hierárquica e nomes de pastas do arquivos  
- Não integra a conversão de imagens e a aplicação de metadados de licenciamento em um único fluxo de trabalho  
- Não implementa técnicas voltadas à restrição de uso por sistemas de IA  

O ARCON foi criado para suprir essas lacunas, com foco na integridade arquivística, na difusão controlada e no uso responsável do conteúdo.
