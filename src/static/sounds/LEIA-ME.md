# Sons do Lucas Garage

Coloque os arquivos **.mp3** nesta pasta com **exatamente estes nomes**.
O app usa o arquivo automaticamente assim que ele existir. Se faltar algum,
ele cai numa síntese limpa — nada quebra.

| Arquivo       | Quando toca                          | Duração ideal |
|---------------|--------------------------------------|---------------|
| `toque.mp3`   | Toque em botões e menu               | 0,1 – 0,2s    |
| `virar.mp3`   | Virar a carta na vitrine             | 0,3 – 0,5s    |
| `curtir.mp3`  | Curtir um carro                      | 0,3 – 0,5s    |
| `motor.mp3`   | Início de partida / abrir garagem    | 0,5 – 1,5s    |
| `intro.mp3`   | Abertura da garagem (entrada do app) | 1 – 2s        |
| `vitoria.mp3` | Ganhou o Super Trunfo                | 1 – 2s        |
| `derrota.mp3` | Perdeu                               | 1 – 2s        |
| `empate.mp3`  | Empate                               | 0,5 – 1s      |

## Onde baixar (grátis e liberado para uso comercial)

- **Pixabay Sound Effects** — pixabay.com/sound-effects (licença própria, uso livre, sem exigir crédito)
- **Mixkit** — mixkit.co/free-sound-effects (grátis, uso comercial permitido)
- **Freesound** — freesound.org (confira a licença de CADA som; prefira os marcados **CC0**)

## Estilo escolhido: iOS (discreto e limpo)

A síntese já está calibrada nesse padrão, então **você só precisa baixar se
quiser refinar ainda mais**. Se for baixar, busque por estes termos:

| Arquivo       | Buscar por                                      |
|---------------|-------------------------------------------------|
| `toque.mp3`   | `ios ui tap`, `soft click ui`, `bubble pop ui`  |
| `virar.mp3`   | `card flip subtle`, `soft swipe whoosh`         |
| `curtir.mp3`  | `ios notification`, `success chime soft`        |
| `motor.mp3`   | `soft transition whoosh`, `ui swoosh`           |
| `intro.mp3`   | `app startup chime`, `soft welcome sound`       |
| `vitoria.mp3` | `apple pay success`, `positive chime bell`      |
| `derrota.mp3` | `soft error tone`, `gentle fail ui`             |
| `empate.mp3`  | `neutral notification`, `single soft bell`      |

**Regra de ouro do estilo iOS:** se o som chamar atenção, está alto demais.
Ele tem que ser percebido, não escutado. Prefira sempre arquivos curtos
(abaixo de 0,5s para interface) e agudos.

## Cuidados

1. **Deixe leve.** Cada arquivo abaixo de 100 KB. Eles carregam junto com a página.
2. **Normalize o volume.** Sons muito altos estouram — o app já reduz para 55%,
   mas arquivos gravados alto continuam agressivos.
3. **Corte o silêncio** do começo do arquivo, senão o som atrasa em relação ao toque.
4. **Guarde a licença.** Se um dia o app for publicado, anote de onde veio cada som.
