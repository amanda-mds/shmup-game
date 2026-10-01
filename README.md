# Nave vs Boss

Jogo de navinha no estilo fliperama dos anos 2000, feito em Python com Pygame. São três fases, cada uma com um boss diferente: um disco voador pilotado por um alienígena, um robô que dispara lasers e um olho gigante que solta tiros que perseguem a nave. Dá para jogar sozinha ou em dupla no mesmo teclado.

Projeto pessoal desenvolvido para praticar Python, Pygame e Programação Orientada a Objetos.

## Funcionalidades

- Modo 1 jogador e modo 2 jogadores cooperativo, no mesmo teclado
- Três fases com bosses diferentes, cada um com quatro padrões de ataque próprios
- Bosses que ficam furiosos na metade da vida: mudam de cor, andam mais rápido e atacam com menos pausa
- Power-ups que caem de tempos em tempos: tiro triplo, escudo e tiro rápido
- Coração que recupera uma vida
- Pontuação com recorde salvo em arquivo, separado por modo de jogo
- Pausa que congela o jogo inteiro, inclusive os tempos dos ataques
- Explosões animadas e tela tremendo nos momentos de impacto
- Sons e música gerados no próprio código, sem nenhum arquivo de áudio
- Gráficos em pixel art desenhados direto no código, sem nenhuma imagem externa
- Fundo animado com estrelas em três camadas de profundidade, lua e meteoros

## Controles

| Ação | 1 jogador | Nave vermelha (2 jogadores) | Nave azul (2 jogadores) |
|------|-----------|-----------------------------|-------------------------|
| Mover | Setas ou WASD | WASD | Setas |
| Atirar | Espaço | Espaço | Enter |

| Tecla | O que faz |
|-------|-----------|
| 1 ou 2 | Escolhe o modo na tela inicial |
| P ou ESC | Pausa e continua |
| N | Liga e desliga o som |
| R | Joga de novo no fim da partida |
| M | Volta para o menu (no fim da partida ou na pausa) |

## Como jogar

Cada nave começa com 3 vidas, mostradas nos cantos de baixo da tela. O objetivo é derrotar os três bosses em sequência. A vida que sobra de uma fase passa para a próxima. No modo em dupla, a partida só termina em derrota quando as duas naves forem destruídas, e uma nave que caiu volta na fase seguinte com 1 vida.

Depois de levar um tiro, a nave fica piscando por 1 segundo sem poder levar dano. A área que leva dano é um pouco menor que o desenho da nave, então um tiro que só raspa na ponta da asa não conta.

### Os bosses

| Fase | Boss | Ataques |
|------|------|---------|
| 1 | Disco Alienígena | Leque de estrelas, estrelas mirando na nave, semicírculo com brecha e parede com buraco |
| 2 | Robô Destruidor | Rajada que varre a tela, laser com aviso, chuva de energia e tiros alternados das garras |
| 3 | Olho Cósmico | Tiros que perseguem a nave, anel com brecha, flor de tiros em ondas e sequência mirada |

### Itens

| Item | Efeito |
|------|--------|
| Coração | Recupera 1 vida. Só é pego por quem perdeu alguma vida |
| Tiro triplo | Atira três tiros em leque por 8 segundos |
| Escudo | Aguenta um tiro sem perder vida |
| Tiro rápido | Atira duas vezes mais rápido por 8 segundos |

Os power-ups ativos aparecem acima das vidas, com uma barrinha mostrando quanto tempo falta.

### Pontuação

| Ação | Pontos |
|------|--------|
| Tiro que acerta o boss | 10 |
| Pegar um item | 100 |
| Derrotar um boss | 1000 x número da fase |
| Cada vida que sobrou ao vencer o jogo | 500 |

O recorde de cada modo fica salvo no arquivo `recordes.json`, criado automaticamente na pasta do jogo.

## Como executar

Pré-requisito: Python 3 instalado.

```bash
# Clone o repositório
git clone https://github.com/SEU-USUARIO/shmup-game.git
cd shmup-game

# (Opcional) Crie e ative um ambiente virtual
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Linux e macOS

# Instale o Pygame
pip install pygame

# Rode o jogo
python main.py
```

## Estrutura do projeto

```
shmup-game/
├── main.py         # Ponto de entrada: cria o jogo e inicia o loop
├── jogo.py         # Classe Jogo: loop principal, estados, fases, colisões, pontuação e telas
├── jogador.py      # Classe Jogador: movimento, tiro, vidas, invencibilidade e power-ups
├── boss.py         # Classe base Boss e o Laser: o que todos os bosses têm em comum
├── bosses.py       # Os três bosses, cada um herdando de Boss com seus próprios ataques
├── tiro.py         # Classe Tiro e TiroTeleguiado (que herda de Tiro e persegue a nave)
├── itens.py        # Classe Item: coração e power-ups que caem
├── explosao.py     # Classe Explosao: animação que toca uma vez e some
├── fundo.py        # Classes Fundo e Meteoro: estrelas, lua e meteoros
├── sons.py         # Classe Sons: efeitos e música sintetizados em Python
├── recordes.py     # Classe Recordes: lê e grava o recorde em JSON
├── relogio.py      # Relógio da partida, que para quando o jogo está pausado
├── sprites.py      # Desenhos em pixel art e as funções que transformam texto em imagem
├── config.py       # Tamanho da tela, cores, controles e valores de dificuldade
└── imagens/        # Imagens usadas neste README
```

## Conceitos aplicados

- **Orientação a Objetos**: cada elemento do jogo é uma classe com responsabilidade própria. As duas naves são instâncias da mesma classe `Jogador`, diferenciadas apenas pelos sprites e controles passados no construtor.
- **Herança e polimorfismo**: `Boss` concentra o comportamento comum (entrar na tela, andar, levar dano, ficar furioso, sortear ataques) e cada boss em `bosses.py` herda dela, definindo só seus atributos e o método `criar_ataques`. O Olho Cósmico também sobrescreve `mover` para flutuar. Da mesma forma, `TiroTeleguiado` herda de `Tiro` e muda apenas o `atualizar`.
- **Separação de responsabilidades**: as classes cuidam do próprio movimento e desenho, enquanto a classe `Jogo` coordena colisões, fases e pontuação.
- **Game loop e máquina de estados**: o ciclo de tratar eventos, atualizar e desenhar roda a 60 quadros por segundo, e o jogo alterna entre menu, jogando, transição, pausado, vitória e derrota.
- **Controle de tempo**: a partida usa um relógio próprio que só avança fora da pausa. Assim nenhum ataque, power-up ou invencibilidade "vence" enquanto o jogo está parado.
- **Ataques em sequência**: os bosses agendam funções para daqui a alguns milissegundos, o que permite rajadas, ondas e varreduras feitas de vários tiros em momentos diferentes.
- **Persistência em arquivo**: os recordes são lidos e gravados em JSON, com tratamento de erro para quando o arquivo não existe ou está corrompido.
- **Trigonometria aplicada**: seno e cosseno para os tiros em ângulo e para o balanço dos itens, e `atan2` para os ataques que miram e para o tiro teleguiado decidir para onde virar.
- **Geração procedural**: as explosões são desenhadas por uma função a partir de círculos de pixels, e os sons e a música são calculados a partir de ondas quadradas, triangulares e ruído.
- **Pixel art gerada por código**: cada sprite é uma lista de textos em que cada letra representa uma cor. A nave vermelha e as versões furiosas dos bosses são geradas a partir dos desenhos originais, apenas trocando as letras.

## Como personalizar

Os principais ajustes ficam no `config.py`: vidas, velocidade das naves, tempo de invencibilidade, frequência e duração dos itens, controles e pontuação. A vida, a velocidade e as pausas entre ataques de cada boss ficam no `bosses.py`.

Para criar um boss novo, basta criar uma classe que herda de `Boss`, definir os sprites e os ataques, e adicionar a classe na lista `FASES` no fim do `bosses.py`:

```python
class MeuBoss(Boss):
    NOME = "MEU BOSS"
    VIDA_POR_JOGADOR = 60
    VELOCIDADE = 3
    SPRITE = sprites.ROBO
    SPRITE_FURIOSO = sprites.ROBO_FURIOSO
    SPRITE_ACERTADO = sprites.ROBO_ACERTADO
    TIRO = sprites.TIRO_ROBO

    def criar_ataques(self):
        return [(self.ataque_chuva_reta, 1000)]

    def ataque_chuva_reta(self, jogadores):
        for angulo in (70, 90, 110):
            self.atirar_em_angulo(angulo, 4)
```

Para mudar o visual de qualquer elemento, basta editar o desenho correspondente no `sprites.py`. Cada letra é uma cor da `PALETA` (`W` é branco, `C` é ciano, `B` é azul) e o ponto é transparente. Todas as linhas de um desenho precisam ter o mesmo tamanho.
## Autora

Amanda Monteiro da Silva
