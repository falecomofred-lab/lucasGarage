"""
Fichas curadas das miniaturas do Lucas — história, curiosidade, peso e produção.

COMO USAR (no seu PC, com o servidor parado):

    python fichas_carros.py            # mostra o que seria preenchido
    python fichas_carros.py --gravar   # grava no banco

REGRA DE SEGURANÇA: só preenche campo VAZIO. Nada que o Lucas escreveu
é sobrescrito. Para forçar por cima, use --forcar.

SOBRE OS NÚMEROS: peso em kg e unidades produzidas são valores de
referência do modelo real, arredondados. Servem para o jogo ficar
equilibrado e coerente — não são medições de uma unidade específica.
O Lucas pode corrigir qualquer carta no editor.
"""

import sys

# nome exato da carta -> ficha
FICHAS = {

    # ═══════════ CLÁSSICOS PRÉ-GUERRA E ANOS 30/50 ═══════════
    "Wanderer W25K Roadster": {
        "peso": 750, "produzidos": 259,
        "descricao": "Roadster esportivo alemão da Wanderer, uma das quatro marcas que formaram a Auto Union — origem da Audi e dos quatro anéis. Motor 2.0 de seis cilindros com compressor, projetado sob supervisão de Ferdinand Porsche.",
        "curiosidade": "Foram feitas apenas 259 unidades entre 1936 e 1938, o que faz dele um dos carros mais raros já produzidos na Alemanha.",
    },
    "540K Roadster": {
        "peso": 2300, "produzidos": 419,
        "descricao": "O topo de linha da Mercedes-Benz nos anos 30, com motor 5.4 de oito cilindros e compressor acionado ao fundo do acelerador. Era o carro dos chefes de Estado e das grandes fortunas europeias.",
        "curiosidade": "O 'K' vem de Kompressor. Ao pisar fundo, o compressor entrava com um assobio característico que anunciava o carro antes de ele aparecer.",
    },
    "Eldorado": {
        "peso": 2200, "produzidos": 6050,
        "descricao": "O Cadillac Eldorado de 1956 é o símbolo do exagero americano do pós-guerra: rabetas de avião, cromo por toda parte e um V8 de 5.9 litros. Media mais de 5,6 metros.",
        "curiosidade": "As rabetas traseiras foram inspiradas no caça P-38 Lightning da Segunda Guerra — a Cadillac queria que o carro parecesse um avião.",
    },
    "Jaguar e Cabriolet": {
        "peso": 1250, "produzidos": 72500,
        "descricao": "O Jaguar E-Type foi lançado em 1961 e redefiniu o que um esportivo podia ser: 240 km/h por uma fração do preço de uma Ferrari. Motor seis cilindros em linha de 4.2 litros.",
        "curiosidade": "Enzo Ferrari o chamou de 'o carro mais bonito já feito'. Há um E-Type exposto no Museu de Arte Moderna de Nova York.",
    },
    "Corvette(Clássico)": {
        "peso": 1370, "produzidos": 21513,
        "descricao": "O Corvette Sting Ray de 1963 trouxe o desenho de Bill Mitchell inspirado em tubarões e a primeira suspensão traseira independente do modelo. V8 de 5.4 litros.",
        "curiosidade": "Só o ano de 1963 teve o vidro traseiro dividido ao meio. Foi retirado em 1964 por atrapalhar a visibilidade — e hoje é justamente o que torna esse ano o mais valorizado.",
    },
    "Cobra": {
        "peso": 1050, "produzidos": 998,
        "descricao": "Carroceria leve inglesa da AC somada a um V8 americano da Ford: a receita simples de Carroll Shelby para vencer a Ferrari nas pistas. Na versão 427, eram 7 litros em um carro de pouco mais de mil quilos.",
        "curiosidade": "A relação peso-potência era tão extrema que a Cobra 427 acelerava de 0 a 100 km/h e voltava a zero em menos de 14 segundos — recorde que durou décadas.",
    },
    "DB5": {
        "peso": 1470, "produzidos": 1059,
        "descricao": "O Aston Martin DB5 é o gran turismo britânico definitivo, com motor seis cilindros de 4.0 litros e carroceria em alumínio feita à mão pela Superleggera.",
        "curiosidade": "Ficou eterno como o carro de James Bond em '007 contra Goldfinger', equipado com placas giratórias, banco ejetável e metralhadoras atrás dos faróis.",
    },
    "Impala": {
        "peso": 1700, "produzidos": 654000,
        "descricao": "O Chevrolet Impala de 1967 é o sedã americano em seu auge de tamanho e presença, com V8 e mais de cinco metros de comprimento.",
        "curiosidade": "O Impala foi o carro mais vendido dos Estados Unidos por vários anos seguidos, e o de 1967 virou ícone da cultura pop ao aparecer na série Supernatural.",
    },
    "Galaxie": {
        "peso": 1750, "produzidos": 92000,
        "descricao": "Fabricado no Brasil a partir de 1967, o Ford Galaxie era o maior e mais luxuoso carro nacional, com V8 de 4.8 litros e ar-condicionado de fábrica.",
        "curiosidade": "Ficou conhecido como o carro das autoridades brasileiras nos anos 70 — ministros e generais andavam de Galaxie preto.",
    },
    "Mustang (Clássico)": {
        "peso": 1250, "produzidos": 607568,
        "descricao": "O Ford Mustang de 1966 criou a categoria pony car: esportivo acessível, com capô longo e traseira curta. Vendeu um milhão de unidades em menos de dois anos.",
        "curiosidade": "No dia do lançamento, em abril de 1964, tanta gente foi às concessionárias que várias tiveram de fechar as portas para conter a multidão.",
    },

    # ═══════════ BRASILEIROS CLÁSSICOS ═══════════
    "Brasília": {
        "peso": 890, "produzidos": 1035000,
        "descricao": "Projetado e fabricado no Brasil sobre a plataforma do Fusca, com motor 1.6 refrigerado a ar atrás. Foi pensado como o carro da família brasileira dos anos 70.",
        "curiosidade": "Chegou a ser exportado para mais de 30 países e foi um dos poucos projetos genuinamente brasileiros da Volkswagen a virar sucesso mundial.",
    },
    "Fusca": {
        "peso": 820, "produzidos": 21529464,
        "descricao": "O carro mais fabricado da história em uma única plataforma. Motor 1.3 ou 1.6 refrigerado a ar, atrás, e mecânica simples o bastante para ser consertada em qualquer lugar do mundo.",
        "curiosidade": "Mais de 21 milhões de unidades saíram das fábricas em quatro décadas. No Brasil, foi produzido de 1959 a 1986, e voltou de 1993 a 1996 por pedido do presidente Itamar Franco.",
    },
    "Fusca (Herbie)": {
        "peso": 820, "produzidos": 21529464,
        "descricao": "Versão do Fusca caracterizada como Herbie, o fusca de corrida branco com o número 53 e faixas azuis e vermelhas, protagonista dos filmes da Disney a partir de 1968.",
        "curiosidade": "O número 53 foi escolhido porque o diretor Robert Stevenson era fã do arremessador Don Drysdale, que usava essa camisa no beisebol.",
    },
    "Fusca (Heineken)": {
        "peso": 820, "produzidos": 21529464,
        "descricao": "Fusca em versão promocional temática, com a pintura verde característica da marca de cerveja. Miniaturas publicitárias como esta são feitas em séries limitadas.",
        "curiosidade": "Fuscas personalizados de marcas viraram objeto de coleção justamente porque nunca foram vendidos em loja — circulavam em ações promocionais.",
    },
    "Fusca (Flamengo)": {
        "peso": 820, "produzidos": 21529464,
        "descricao": "Fusca temático nas cores do Flamengo, parte da leva de miniaturas de clubes brasileiros que fizeram sucesso entre colecionadores.",
        "curiosidade": "A união entre Fusca e futebol não é à toa: nos anos 70 e 80, era o carro que levava a torcida ao estádio em todo o Brasil.",
    },
    "Fusca (Chamas)": {
        "peso": 820, "produzidos": 21529464,
        "descricao": "Fusca com pintura customizada de chamas, estilo hot rod, referência à cultura de personalização americana aplicada ao carro popular alemão.",
        "curiosidade": "A pintura de chamas nasceu nos hot rods dos anos 50 e virou marca registrada das customizações — o Fusca é um dos carros mais modificados do mundo.",
    },
    "Fusca (Conversível)": {
        "peso": 870, "produzidos": 331847,
        "descricao": "Versão conversível do Fusca, produzida pela carroceria Karmann com capota de lona e estrutura reforçada para compensar a ausência do teto.",
        "curiosidade": "A capota tinha três camadas e era tão bem feita que o conversível era mais silencioso que muitos sedãs da época.",
    },
    "Chevette": {
        "peso": 900, "produzidos": 1600000,
        "descricao": "Lançado no Brasil em 1973 sobre a plataforma global T-Car da GM, com motor 1.4 e tração traseira. Foi o compacto de entrada da Chevrolet por duas décadas.",
        "curiosidade": "A mesma plataforma virou Opel Kadett na Europa, Isuzu Gemini no Japão e Pontiac T1000 nos EUA — um dos projetos mais reaproveitados da história.",
    },
    "Corcel": {
        "peso": 950, "produzidos": 900000,
        "descricao": "Nasceu de um projeto da Willys em parceria com a Renault, herdado pela Ford após a compra da Willys brasileira. Motor 1.4 de origem francesa e tração dianteira, incomum no Brasil da época.",
        "curiosidade": "O nome veio de um concurso interno. Como o projeto era secreto, era chamado apenas de 'M-380' até o lançamento.",
    },
    "Maverick GT": {
        "peso": 1300, "produzidos": 108000,
        "descricao": "Versão brasileira do cupê americano, com V8 de 4.9 litros — o famoso 302. Era um dos carros mais potentes vendidos no país nos anos 70.",
        "curiosidade": "O Maverick GT brasileiro ficou marcado pelas faixas pretas no capô e pelo consumo lendário: fazia cerca de quatro quilômetros por litro.",
    },
    "Opala": {
        "peso": 1150, "produzidos": 1000000,
        "descricao": "Primeiro automóvel de passeio da Chevrolet do Brasil, com carroceria derivada do Opel Rekord e motores de quatro e seis cilindros de origem americana.",
        "curiosidade": "O nome é a junção de Opel com Impala, as duas origens do projeto. O seis cilindros 4.1 virou lenda entre os preparadores brasileiros.",
    },
    "Veraneio": {
        "peso": 1900, "produzidos": 120000,
        "descricao": "Perua grande da Chevrolet brasileira, derivada da picape C-10, com espaço para até nove pessoas. Serviu como ambulância, viatura e carro de fazenda por décadas.",
        "curiosidade": "Foi a viatura policial mais icônica do Brasil nos anos 70 e 80 — a 'Veraneio da polícia' entrou para o imaginário nacional.",
    },
    "C15": {
        "peso": 1600, "produzidos": 200000,
        "descricao": "Picape da linha Série 10 da Chevrolet brasileira, irmã da C-10 e da C-14, com motor a diesel ou a gasolina e chassi de longarinas.",
        "curiosidade": "A numeração indicava a capacidade e a configuração: a família C-10, C-14 e C-15 dominou o trabalho pesado no campo brasileiro.",
    },
    "F-100": {
        "peso": 1550, "produzidos": 180000,
        "descricao": "Picape da Ford produzida no Brasil, robusta e de mecânica simples, com motor seis cilindros ou V8. Virou símbolo do trabalho rural.",
        "curiosidade": "A F-100 brasileira usava a cabine do modelo americano dos anos 60 muito depois de ele ter sido substituído nos EUA — ficou em linha até 1992.",
    },
    "147": {
        "peso": 750, "produzidos": 1200000,
        "descricao": "O primeiro carro da Fiat no Brasil, lançado em 1976 em Betim. Compacto, leve e com motor 1.05 de tração dianteira.",
        "curiosidade": "Foi o primeiro carro do mundo a sair de fábrica movido a álcool, em 1979 — uma resposta brasileira à crise do petróleo.",
    },
    "Uno": {
        "peso": 800, "produzidos": 8800000,
        "descricao": "Projetado por Giorgetto Giugiaro, o Uno trouxe desenho alto e quadrado que maximizava o espaço interno. No Brasil, ficou em linha por incríveis 29 anos.",
        "curiosidade": "A versão Mille, com motor 1.0, foi o carro mais vendido do Brasil por vários anos e ajudou a criar a categoria dos populares.",
    },
    "Gol GT-I": {
        "peso": 900, "produzidos": 60000,
        "descricao": "Versão esportiva do Gol com injeção eletrônica e motor 1.8, uma das primeiras aplicações da tecnologia em carros nacionais no fim dos anos 80.",
        "curiosidade": "O GTI foi o carro dos sonhos de uma geração de brasileiros — era o esportivo acessível numa época de mercado fechado às importações.",
    },
    "Santana": {
        "peso": 1050, "produzidos": 1000000,
        "descricao": "Sedã médio da Volkswagen brasileira, derivado do Passat europeu, com motor 1.8 ou 2.0 e reputação de durabilidade.",
        "curiosidade": "Foi o carro oficial do governo brasileiro por muitos anos e chegou a ser produzido na China, onde continuou em linha bem depois de sair daqui.",
    },
    "parati": {
        "peso": 950, "produzidos": 700000,
        "descricao": "Perua derivada do Gol, com o mesmo motor e mecânica, mas porta-malas ampliado. Foi a station wagon mais popular do Brasil.",
        "curiosidade": "O nome vem da cidade histórica de Paraty, no Rio — a Volkswagen do Brasil batizava seus modelos com nomes de lugares e ventos.",
    },
    "Passat": {
        "peso": 1000, "produzidos": 400000,
        "descricao": "Versão brasileira do Passat da Volkswagen, com motor refrigerado a água e tração dianteira, novidades para o mercado nacional dos anos 70 e 80.",
        "curiosidade": "A versão TS brasileira era considerada esportiva na época e disputava as ruas com o Maverick e o Opala.",
    },
    "Kombi": {
        "peso": 1200, "produzidos": 1500000,
        "descricao": "Produzida no Brasil de 1957 a 2013 — 56 anos sem parar. Serviu de van escolar, ambulância, food truck e casa sobre rodas.",
        "curiosidade": "O Brasil foi o último país do mundo a fabricar a Kombi. A produção só terminou porque a lei passou a exigir airbag e freios ABS.",
    },
    "Kombi (Coca-Cola)": {
        "peso": 1200, "produzidos": 1500000,
        "descricao": "Kombi em versão promocional da Coca-Cola, com a pintura vermelha e branca usada nas frotas de distribuição da marca.",
        "curiosidade": "Kombis de entrega da Coca-Cola foram usadas de verdade no Brasil por décadas e hoje são das miniaturas mais procuradas por colecionadores.",
    },
    "Gurgel BR 800": {
        "peso": 640, "produzidos": 4500,
        "descricao": "Microcarro totalmente projetado e fabricado no Brasil por João Augusto Conrado do Amaral Gurgel, com motor dois cilindros de 800 cm³ e carroceria em plástico reforçado.",
        "curiosidade": "Foi financiado por uma emissão de ações vendidas ao público — milhares de brasileiros compraram um pedaço da fábrica para o carro existir.",
    },
    "Puma GTS": {
        "peso": 780, "produzidos": 22000,
        "descricao": "Esportivo brasileiro com carroceria de fibra de vidro sobre mecânica de Fusca ou Chevrolet. Feito em São Paulo, foi exportado para dezenas de países.",
        "curiosidade": "O Puma foi vendido em kit em alguns mercados: o comprador recebia a carroceria e montava sobre a plataforma de um Fusca.",
    },
    "Bugre": {
        "peso": 600, "produzidos": 8000,
        "descricao": "Buggy brasileiro de fibra de vidro sobre plataforma de Fusca, criado para a areia das praias do litoral. O nome virou sinônimo da categoria no Brasil.",
        "curiosidade": "O buggy nasceu na Califórnia, mas foi no Brasil que ele virou fenômeno — as praias do Nordeste têm frotas inteiras até hoje.",
    },
    "Willys": {
        "peso": 1100, "produzidos": 130000,
        "descricao": "O Jeep Willys brasileiro, fabricado pela Willys-Overland e depois pela Ford, com motor seis cilindros e tração 4x4. Abriu estradas pelo interior do país.",
        "curiosidade": "O Jeep original nasceu na Segunda Guerra Mundial. O nome viria de 'GP', de General Purpose, pronunciado rapidamente em inglês.",
    },
    "Willys (Exército)": {
        "peso": 1100, "produzidos": 130000,
        "descricao": "Versão militar do Jeep Willys, na pintura verde-oliva usada pelas forças armadas. Foi o veículo de campo padrão por décadas.",
        "curiosidade": "Na Segunda Guerra foram produzidos mais de 600 mil Jeeps. Eisenhower disse que os EUA não teriam vencido a guerra sem ele.",
    },
    "Willys Dauphine": {
        "peso": 630, "produzidos": 90000,
        "descricao": "Versão brasileira do Renault Dauphine, montada pela Willys-Overland do Brasil, com motor traseiro de 845 cm³.",
        "curiosidade": "No Brasil ganhou o apelido de 'Dauphine Teimoso' na versão esportiva Gordini, por insistir em andar mais do que o motor pequeno sugeria.",
    },
    "Willys Gordini": {
        "peso": 650, "produzidos": 40000,
        "descricao": "Versão preparada do Dauphine com acerto do engenheiro francês Amédée Gordini, conhecido como 'o feiticeiro' pelos ajustes que fazia em motores.",
        "curiosidade": "Gordini aumentava a potência com técnicas artesanais de preparação e virou lenda na França — o nome dele ainda batiza versões esportivas da Renault.",
    },
    "DKW": {
        "peso": 900, "produzidos": 110000,
        "descricao": "Fabricado no Brasil pela Vemag, o DKW-Vemag tinha motor de dois tempos e três cilindros, além de tração dianteira — raridade no país nos anos 60.",
        "curiosidade": "O motor de dois tempos tinha apenas sete partes móveis e soltava fumaça azulada característica, porque o óleo era misturado à gasolina.",
    },
    "Dart": {
        "peso": 1600, "produzidos": 65000,
        "descricao": "Cupê da Dodge produzido no Brasil com V8 de 5.2 litros. Era um dos carros mais potentes e caros do mercado nacional nos anos 70.",
        "curiosidade": "O Dart brasileiro tinha um V8 tão grande que a fábrica precisou reforçar a suspensão dianteira em relação ao projeto original.",
    },
    "Karmann-ghia": {
        "peso": 820, "produzidos": 445000,
        "descricao": "Mecânica de Fusca sob uma carroceria desenhada pela italiana Ghia e produzida à mão pela alemã Karmann. Bonito por fora, simples por baixo.",
        "curiosidade": "A carroceria era soldada e lixada manualmente, sem estampos grandes — por isso nenhum Karmann-Ghia é exatamente igual ao outro.",
    },
    "FNM JK 2000": {
        "peso": 1350, "produzidos": 12000,
        "descricao": "Sedã produzido pela Fábrica Nacional de Motores sob licença da Alfa Romeo, com motor 2.0 de quatro cilindros e duplo comando.",
        "curiosidade": "O 'JK' é uma homenagem a Juscelino Kubitschek. Era considerado o carro de luxo nacional e concorria com o Galaxie e o Opala.",
    },
    "280 S": {
        "peso": 1500, "produzidos": 93000,
        "descricao": "Sedã da Mercedes-Benz da geração W108, com motor seis cilindros em linha de 2.8 litros e acabamento em madeira e couro.",
        "curiosidade": "Essa geração ficou conhecida pela robustez: muitos exemplares ultrapassaram um milhão de quilômetros ainda com o motor original.",
    },
    "500 SL": {
        "peso": 1900, "produzidos": 204940,
        "descricao": "Roadster da Mercedes-Benz da geração R129, com V8 de 5.0 litros, capota elétrica e santantônio que subia sozinho em caso de capotamento.",
        "curiosidade": "Foi o primeiro carro do mundo com barra anticapotamento automática: sensores disparavam a estrutura em três décimos de segundo.",
    },
    "911 (Clássico)": {
        "peso": 1120, "produzidos": 21000,
        "descricao": "O Porsche 911 da geração 930 trouxe o turbo e o aerofólio traseiro conhecido como 'rabo de baleia'. Motor bóxer seis cilindros refrigerado a ar, atrás.",
        "curiosidade": "Ganhou o apelido de 'viúva negra' porque o turbo entrava de forma abrupta no meio das curvas, surpreendendo motoristas desavisados.",
    },
    "911 Carrera 2 (Clássico)": {
        "peso": 1350, "produzidos": 55000,
        "descricao": "Porsche 911 Carrera com motor bóxer refrigerado a ar, a configuração que definiu a marca por mais de trinta anos.",
        "curiosidade": "O 911 é um dos poucos carros do mundo produzidos continuamente desde os anos 60 mantendo o motor atrás do eixo traseiro.",
    },
    "Miura": {
        "peso": 1245, "produzidos": 764,
        "descricao": "Considerado o primeiro supercarro moderno, o Miura colocou um V12 de 4.0 litros transversal no meio do carro, atrás do motorista. Desenho de Marcello Gandini aos 25 anos.",
        "curiosidade": "Ferruccio Lamborghini era fabricante de tratores e criou a marca depois de uma discussão com Enzo Ferrari sobre a embreagem de um Ferrari que ele possuía.",
    },
    "Countach": {
        "peso": 1490, "produzidos": 1999,
        "descricao": "Sucessor do Miura, com desenho em cunha e portas tesoura que viraram assinatura da Lamborghini. Motor V12 longitudinal central.",
        "curiosidade": "'Countach' é uma expressão do dialeto piemontês que se diz diante de algo impressionante — foi o que um operário exclamou ao ver o protótipo.",
    },

    # ═══════════ SUPERESPORTIVOS MODERNOS ═══════════
    "LaFerrari": {
        "peso": 1430, "produzidos": 499,
        "descricao": "O primeiro híbrido da Ferrari: V12 de 6.3 litros somado a um motor elétrico derivado da Fórmula 1, totalizando 963 cv. Chassi inteiro em fibra de carbono.",
        "curiosidade": "As 499 unidades foram vendidas antes mesmo da apresentação oficial, e a Ferrari escolhia os compradores — não bastava ter dinheiro, era preciso convite.",
    },
    "Sián": {
        "peso": 1560, "produzidos": 63,
        "descricao": "Primeiro Lamborghini híbrido, com V12 de 6.5 litros e 819 cv. Usa supercapacitor em vez de bateria, tecnologia mais leve e de resposta mais rápida.",
        "curiosidade": "'Sián' significa relâmpago no dialeto de Bolonha. Foram só 63 unidades, número escolhido por causa de 1963, ano de fundação da Lamborghini.",
    },
    "Urus": {
        "peso": 2200, "produzidos": 20000,
        "descricao": "O SUV da Lamborghini, com V8 biturbo de 4.0 litros e 650 cv. Acelera de 0 a 100 km/h em 3,6 segundos, apesar das mais de duas toneladas.",
        "curiosidade": "O Urus dobrou a produção anual da Lamborghini e financiou o desenvolvimento dos superesportivos V12 da marca.",
    },
    "FXX K": {
        "peso": 1165, "produzidos": 40,
        "descricao": "Versão de pista da LaFerrari, sem homologação para ruas. O sistema híbrido rende 1050 cv e a aerodinâmica gera o dobro de carga aerodinâmica do modelo de rua.",
        "curiosidade": "Os donos não podem levar o carro para casa: a Ferrari guarda todos e só os leva a eventos exclusivos em autódromos, com equipe própria.",
    },
    "Evora": {
        "peso": 1383, "produzidos": 6000,
        "descricao": "Esportivo da Lotus com motor V6 3.5 de origem Toyota montado atrás dos bancos e chassi de alumínio colado. Foi o primeiro Lotus com quatro lugares em muitos anos.",
        "curiosidade": "Colin Chapman, fundador da Lotus, resumia sua engenharia numa frase: 'simplifique, depois adicione leveza'. O Evora pesa menos que quase todo esportivo de potência equivalente.",
    },
    "Alfieri Concept": {
        "peso": 1600, "produzidos": 1,
        "descricao": "Conceito apresentado pela Maserati em 2014 para celebrar os cem anos da marca, com motor V6 e proporções clássicas de gran turismo.",
        "curiosidade": "O nome homenageia Alfieri Maserati, o mais velho dos irmãos que fundaram a empresa em Bolonha, em 1914.",
    },
    "3.0 CSL Hommage R": {
        "peso": 1200, "produzidos": 1,
        "descricao": "Conceito da BMW que homenageia o 3.0 CSL dos anos 70, o lendário 'Batmobile' das pistas europeias. Fibra de carbono por toda a carroceria.",
        "curiosidade": "O CSL original ganhou aerofólios tão grandes que foram proibidos nas ruas alemãs — vinham no porta-malas para o dono instalar na pista.",
    },

    # ═══════════ ESPORTIVOS E MODERNOS ═══════════
    "Camaro ZL1": {
        "peso": 1880, "produzidos": 3500,
        "descricao": "A versão mais radical do Camaro, com V8 6.2 supercharged de 580 cv, suspensão magnética e freios Brembo.",
        "curiosidade": "O nome ZL1 vem de um bloco de motor experimental em alumínio dos anos 60, do qual a Chevrolet fez apenas 69 unidades.",
    },
    "M4": {
        "peso": 1572, "produzidos": 40000,
        "descricao": "Cupê esportivo da divisão M da BMW, com seis cilindros em linha biturbo de 3.0 litros e 431 cv. Sucessor direto do M3 cupê.",
        "curiosidade": "Em 2014 a BMW separou os nomes: o sedã seguiu como M3 e o cupê virou M4, encerrando três décadas de M3 de duas portas.",
    },
    "Skyline GT-R R35": {
        "peso": 1740, "produzidos": 48000,
        "descricao": "O Nissan GT-R R35 tem V6 biturbo de 3.8 litros montado à mão e tração integral. Ganhou o apelido de Godzilla por bater carros muito mais caros.",
        "curiosidade": "Cada motor é montado por um único especialista, chamado Takumi, que assina uma placa de alumínio fixada no bloco.",
    },
    "Skyline GT-R": {
        "peso": 1560, "produzidos": 11578,
        "descricao": "O Skyline GT-R R34, com motor RB26DETT de 2.6 litros biturbo e tração integral inteligente ATTESA.",
        "curiosidade": "Ficou mundialmente famoso pelos jogos Gran Turismo e pela série Velozes e Furiosos, virando o carro japonês mais desejado de uma geração.",
    },
    "Skyline GT-R R34": {
        "peso": 1560, "produzidos": 11578,
        "descricao": "O Skyline GT-R R34, com motor RB26DETT de 2.6 litros biturbo e tração integral inteligente ATTESA.",
        "curiosidade": "Ficou mundialmente famoso pelos jogos Gran Turismo e pela série Velozes e Furiosos, virando o carro japonês mais desejado de uma geração.",
    },
    "Supra MK4": {
        "peso": 1570, "produzidos": 45000,
        "descricao": "A quarta geração do Toyota Supra trouxe o motor 2JZ-GTE de 3.0 litros biturbo, famoso por aguentar o dobro da potência original sem abrir o bloco.",
        "curiosidade": "O bloco do 2JZ é tão reforçado que preparadores extraem mais de mil cavalos dele mantendo as peças internas de fábrica.",
    },
    "Z8": {
        "peso": 1585, "produzidos": 5703,
        "descricao": "Roadster da BMW com desenho retrô inspirado no 507 dos anos 50, motor V8 de 4.9 litros vindo do M5 e carroceria de alumínio.",
        "curiosidade": "Apareceu em '007 — O Mundo Não é o Bastante' e foi serrado ao meio por um helicóptero numa das cenas mais dolorosas para entusiastas.",
    },
    "Mustang": {
        "peso": 1600, "produzidos": 300000,
        "descricao": "Geração do Mustang com desenho retrô que resgatou as linhas do modelo de 1967, com V8 de 4.6 litros.",
        "curiosidade": "O Mustang é o carro esportivo mais vendido da história, com mais de dez milhões de unidades desde 1964.",
    },
    "Plymouth GTX": {
        "peso": 1700, "produzidos": 15000,
        "descricao": "Muscle car americano da Plymouth, com V8 de grande cilindrada e postura de cupê pesado. Era vendido como 'o muscle car do executivo'.",
        "curiosidade": "A Plymouth deixou de existir em 2001, quando a Chrysler encerrou a marca depois de mais de setenta anos.",
    },
    "Mini Cooper": {
        "peso": 1160, "produzidos": 400000,
        "descricao": "Geração moderna do Mini sob a BMW, mantendo a proporção de rodas nos extremos e o comportamento ágil que consagrou o original.",
        "curiosidade": "O Mini original de 1959 foi projetado por Alec Issigonis em resposta à crise do petróleo de Suez, e virou ícone ao vencer o Rali de Monte Carlo três vezes.",
    },

    # ═══════════ POPULARES E UTILITÁRIOS MODERNOS ═══════════
    "Golf GT-I": {
        "peso": 960, "produzidos": 470000,
        "descricao": "O Golf GTI criou a categoria hot hatch: um hatch comum com motor de esportivo, suspensão baixa e detalhes vermelhos.",
        "curiosidade": "Nasceu de um projeto paralelo feito por engenheiros da Volkswagen fora do horário, sem autorização da diretoria.",
    },
    "500": {
        "peso": 930, "produzidos": 2000000,
        "descricao": "Releitura moderna do Fiat 500 de 1957, mantendo as proporções compactas e o desenho arredondado do original italiano.",
        "curiosidade": "O 500 original tinha apenas 13 cv e dois cilindros, mas motorizou a Itália inteira no pós-guerra.",
    },
    "500 (Herbie)": {
        "peso": 930, "produzidos": 2000000,
        "descricao": "Fiat 500 em caracterização inspirada no Herbie, com o número 53 e as faixas de corrida do fusca dos filmes da Disney.",
        "curiosidade": "Miniaturas com temática de cinema aplicadas a modelos diferentes do original são feitas em séries curtas e viram item de colecionador.",
    },
    "New Beetle": {
        "peso": 1230, "produzidos": 1200000,
        "descricao": "O New Beetle resgatou a silhueta arredondada do Fusca, mas com motor à frente, tração dianteira e plataforma do Golf.",
        "curiosidade": "Vinha com um vasinho de flores no painel de fábrica — detalhe que virou marca registrada do modelo.",
    },
    "Punto": {
        "peso": 1050, "produzidos": 9000000,
        "descricao": "Hatch compacto da Fiat, produzido também no Brasil a partir de 2007, com motores 1.4 e 1.8 e desenho assinado pela Giugiaro.",
        "curiosidade": "O Punto foi eleito Carro do Ano na Europa em 1995 e vendeu mais de nove milhões de unidades em três gerações.",
    },
    "Astra": {
        "peso": 1200, "produzidos": 500000,
        "descricao": "Hatch médio da Chevrolet derivado do Opel Astra europeu, montado no Brasil com motores 2.0 e reputação de bom acerto de suspensão.",
        "curiosidade": "O Astra brasileiro era conhecido pelo comportamento em curvas superior ao dos concorrentes, herança direta do acerto alemão da Opel.",
    },
    "Corolla": {
        "peso": 1300, "produzidos": 50000000,
        "descricao": "O carro mais vendido da história: mais de 50 milhões de unidades desde 1966. Reputação construída sobre confiabilidade e baixo custo de manutenção.",
        "curiosidade": "Um Corolla é vendido a cada 15 segundos em algum lugar do mundo, em média.",
    },
    "Clio": {
        "peso": 1090, "produzidos": 15000000,
        "descricao": "Hatch compacto da Renault, fabricado no Brasil em São José dos Pinhais. Foi um dos populares mais vendidos do país nos anos 2000.",
        "curiosidade": "A versão Clio Williams, feita em homenagem à equipe de Fórmula 1, é hoje um dos hot hatches mais valorizados entre colecionadores europeus.",
    },
    "Doblo": {
        "peso": 1300, "produzidos": 1500000,
        "descricao": "Utilitário da Fiat com carroceria alta e sete lugares, muito usado como veículo de trabalho e transporte familiar no Brasil.",
        "curiosidade": "O Doblò foi eleito Van Internacional do Ano em 2001 e serviu de base para ambulâncias e veículos adaptados no mundo todo.",
    },
    "Sprinter": {
        "peso": 2200, "produzidos": 4000000,
        "descricao": "Van de carga e passageiros da Mercedes-Benz, lançada em 1995 e presente em mais de 130 países. Serve de base para ambulâncias, motorhomes, escolares e vans de entrega.",
        "curiosidade": "A Sprinter praticamente criou a categoria das vans altas na Europa, e virou a preferida das conversões em motorhome pelo mundo todo.",
    },

    # ═══════════ PICAPES E FORA DE ESTRADA ═══════════
    "Defender 90": {
        "peso": 2200, "produzidos": 80000,
        "descricao": "A reinvenção do Defender pela Land Rover, com monobloco de alumínio no lugar do chassi de longarinas, mantendo a silhueta reta do original.",
        "curiosidade": "O Defender antigo ficou 67 anos praticamente sem mudar de forma — a versão nova foi a primeira reformulação profunda desde 1948.",
    },
    "Gladiator": {
        "peso": 2200, "produzidos": 90000,
        "descricao": "A picape do Jeep Wrangler, com caçamba integrada, teto e portas removíveis e capacidade real de fora de estrada.",
        "curiosidade": "É a única picape do mercado americano com para-brisa rebatível e teto removível de fábrica.",
    },
    "Cherokee": {
        "peso": 1900, "produzidos": 200000,
        "descricao": "SUV médio do Jeep, com tração integral e sistemas eletrônicos de controle de tração para diferentes tipos de terreno.",
        "curiosidade": "O Cherokee XJ dos anos 80 é considerado o primeiro SUV moderno: foi ele que popularizou a ideia de utilitário com conforto de carro.",
    },
    "H2": {
        "peso": 2900, "produzidos": 100000,
        "descricao": "Versão civil do Hummer militar, com quase três toneladas, V8 de 6.0 litros e consumo que virou símbolo do exagero americano dos anos 2000.",
        "curiosidade": "O Hummer original, o H1, foi criado para o Exército dos EUA e ganhou versão de rua depois que Arnold Schwarzenegger convenceu a fabricante a vendê-lo.",
    },
    "Jimny": {
        "peso": 1090, "produzidos": 3000000,
        "descricao": "Fora de estrada compacto da Suzuki, com chassi de longarinas, tração 4x4 com reduzida e menos de 1100 kg — leveza que compensa a pouca potência.",
        "curiosidade": "Por ser pequeno e leve, o Jimny passa em trilhas onde utilitários grandes não entram, e tem culto entre off-roaders no mundo todo.",
    },
    "Hilux": {
        "peso": 2100, "produzidos": 20000000,
        "descricao": "A picape média da Toyota, com fama mundial de indestrutível. Chassi de longarinas, motor a diesel e presença em mais de 180 países.",
        "curiosidade": "O programa Top Gear tentou destruir uma Hilux afogando, incendiando e colocando no topo de um prédio demolido — e ela ainda pegou no motor de partida.",
    },
    "F-150": {
        "peso": 2000, "produzidos": 40000000,
        "descricao": "A picape mais vendida dos Estados Unidos por mais de quatro décadas seguidas. A partir de 2015, passou a usar carroceria de alumínio para reduzir peso.",
        "curiosidade": "A Ford vende cerca de uma F-150 por minuto nos Estados Unidos. É o veículo mais lucrativo da indústria automotiva americana.",
    },
    "K5": {
        "peso": 1500, "produzidos": 300000,
        "descricao": "Sedã médio da Kia, conhecido como Optima em vários mercados, com desenho assinado por Peter Schreyer.",
        "curiosidade": "Schreyer veio da Audi, onde desenhou o TT, e foi o responsável por transformar a identidade visual da Kia a partir de 2006.",
    },
    "Lançar Evolution": {
        "peso": 1600, "produzidos": 150000,
        "descricao": "O Mitsubishi Lancer Evolution nasceu para homologar a marca no Mundial de Rali, com motor 2.0 turbo e tração integral com controle ativo de guinada.",
        "curiosidade": "O nome desta carta está com erro de digitação: o correto é Lancer Evolution. Foi rival direto do Subaru Impreza WRX nas pistas de rali dos anos 90 e 2000.",
    },

    # ═══════════ TEMÁTICOS ═══════════
    "Taurus Polícia (Nova York)": {
        "peso": 1850, "produzidos": 8000000,
        "descricao": "Ford Taurus em versão Police Interceptor, caracterizado como viatura do Departamento de Polícia de Nova York, com pintura branca e azul e a inscrição NYPD.",
        "curiosidade": "O Taurus Police Interceptor substituiu o Crown Victoria nas polícias americanas a partir de 2012, encerrando três décadas de reinado do sedã de chassi de longarinas.",
    },
    "Táxi (Nova York)": {
        "peso": 1700, "produzidos": 200000,
        "descricao": "O clássico táxi amarelo de Nova York, um dos símbolos visuais mais reconhecíveis da cidade.",
        "curiosidade": "O amarelo foi escolhido em 1907 por John Hertz, que se baseou em um estudo apontando essa como a cor mais visível à distância.",
    },
}


# Grafias antigas que ainda existem em algum banco -> ficha equivalente.
# (o servidor e a cópia local divergiram em cinco nomes)
APELIDOS = {
    "New Beatle": "New Beetle",
    "Emira": "Evora",
    "Polícia (Nova York)": "Taurus Polícia (Nova York)",
    "Carrera 2 (Clássico)": "911 Carrera 2 (Clássico)",
    "Spring": "Sprinter",
    "Skyline GT-R": "Skyline GT-R R34",
}
for _antigo, _novo in APELIDOS.items():
    if _novo in FICHAS and _antigo not in FICHAS:
        FICHAS[_antigo] = FICHAS[_novo]


def main():
    gravar = "--gravar" in sys.argv
    forcar = "--forcar" in sys.argv

    from src.infra.database import SessionLocal, CarModel, Base, engine
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        carros = db.query(CarModel).order_by(CarModel.id).all()
        por_nome = {}
        for c in carros:
            por_nome.setdefault((c.name or "").strip(), []).append(c)

        print("=" * 74)
        print("FICHAS — %s" % ("GRAVANDO" if gravar else "SIMULAÇÃO (nada será salvo)"))
        if forcar:
            print("MODO FORÇAR: sobrescreve textos que já existem")
        print("=" * 74)

        aplicadas = faltando = 0
        for nome, ficha in FICHAS.items():
            alvos = por_nome.get(nome)
            if not alvos:
                print("  ?  %-28s (não achei carta com esse nome)" % nome[:28])
                continue
            for c in alvos:
                mudou = []
                if ficha.get("peso") and (forcar or not c.peso):
                    if gravar:
                        c.peso = ficha["peso"]
                    mudou.append("peso")
                if ficha.get("produzidos") and (forcar or not c.produzidos):
                    if gravar:
                        c.produzidos = ficha["produzidos"]
                    mudou.append("produzidos")
                if ficha.get("descricao") and (forcar or not (c.description or "").strip()):
                    if gravar:
                        c.description = ficha["descricao"]
                    mudou.append("história")
                if ficha.get("curiosidade") and (forcar or not (c.trivia or "").strip()):
                    if gravar:
                        c.trivia = ficha["curiosidade"]
                    mudou.append("curiosidade")

                if mudou:
                    aplicadas += 1
                    print("  ✓  %-28s %s" % (nome[:28], ", ".join(mudou)))
                else:
                    print("  ·  %-28s (já preenchido)" % nome[:28])

        # quais cartas do banco ainda não têm ficha aqui
        sem_ficha = [c.name for c in carros if (c.name or "").strip() not in FICHAS]
        faltando = len(sem_ficha)

        if gravar:
            db.commit()
            print("\n✅ %d cartas atualizadas." % aplicadas)
        else:
            print("\n(simulação — rode com --gravar para salvar)")

        if sem_ficha:
            print("\n%d cartas ainda sem ficha nesta tabela:" % faltando)
            for n in sem_ficha:
                print("   -", n)
    finally:
        db.close()


if __name__ == "__main__":
    main()
