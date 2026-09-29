# 17. Game Theory

> Источник: Patrick M. Emerson, *Intermediate Microeconomics*, Oregon State University, 2019. https://open.oregonstate.education/intermediatemicroeconomics/chapter/module-17/
> Лицензия: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/) — только некоммерческое использование, с указанием автора, производные — под той же лицензией. Текст сконвертирован в markdown без изменений по смыслу; формулы — LaTeX в `$...$`; рисунки — ссылками.

### The Policy Question
 **Do We Need to Regulate Banks to Save Them from Themselves?**

In the real estate and banking crisis that caused the United States to fall into the worst recession since the Great Depression, banks were seen to have engaged in reckless and risky behavior that was seemingly against their self-interest. Part of the risky behavior was attributed to the relaxation of banking regulations, particularly those that separated commercial banks from investment banks. But the question of why banks would engage in self-destructive behavior in the first place is one that puzzles many observers who have a background in economics and knows that free markets often direct individual self-interested action toward the good of society.

One possible explanation for this disconnect is the possibility that the banking industry is much more strategic than policy makers understood. The strategic incentives to take risks could be a lot more powerful than generally appreciated. The nature of this strategic environment and the incentives it provides are essential to understand to be able to make appropriate and effective policies.

### Exploring the Policy Question

1. What are the strategic incentives for banks to take risks?
2. What policy solutions present themselves from this analysis?

**[Learning Objectives]**

#### 17.1 What Is Game Theory?

**Learning Objective 17.1**: Describe game theory and the types of situations it describes.

#### 17.2 Single Play Games

**Learning Objective 17.2**: Describe normal form games, and identify optimal strategies and equilibrium outcomes in such games.

#### 17.3 Sequential Games

**Learning Objective 17.3**: Describe sequential move games, and explain how they are solved.

#### 17.4 Repeated Games

**Learning Objective 17.4**: Describe repeated games and the difference between finitely repeated games and infinitely repeated games and their equilibrium.

#### 17.5 Policy Example
 **Do We Need to Regulate Banks to Save Them from Themselves?**

**Learning Objective 17.5**: Explain how game theory can be used to understand the banking collapse of 2008.

### 17.1 What Is Game Theory?

**Learning Objective 17.1**: Describe game theory and the types of situations it describes.

Until this chapter, we have studied economic decision-making in situations where an agent’s payoff is based on their actions alone. In other words, the payoff to an agent’s actions is known, and the trick is to figure out how to get the highest payoff. But there are many situations in which the payoffs to an agent’s actions are determined in part by the actions of other agents. Consider this simple example: On Saturday, you know there are a number of parties happening in and around your school. How much you will enjoy attending any one party is in large part determined by how many of your friends will be there. In other words, your payoff is a function of not only your decision about which party to attend but also the decisions of your friends. We call these types of interactions **strategic interactions**, where agents must anticipate the actions of others when making decisions, and we use game theory to model them so that we can think about the outcomes of these interactions just like we think about outcomes in markets without strategic interaction, like the price and quantity outcome in a product market. **Game theory** is the study of strategic interactions among economic agents.

Game theory is extremely useful because it allows us to anticipate the behavior of economic agents within a game and the outcomes of strategic games. Game theory gets its name from actual games. Checkers and chess are strategic games where two players interact, and the outcome of the game is determined by the actions of both players. In economics, game theory is particularly useful in understanding imperfectly competitive markets like oligopoly—the subject of the next chapter—because the price and output decisions of one firm affect the demand and therefore profit function of the other firms. But before we can study oligopoly markets, we must first understand games and how to analyze them. In this chapter, we will consider only **non-cooperative games**, games where the players are not able to negotiate and make binding agreements within the game. An example of a cooperative game might be one where two poker players agree to share winnings no matter who actually wins; as a result, their strategies are based on how best to maximize the joint expected payoff, not individual payoffs.

All games have three basic elements: players, strategies, and payoffs. The **players** of the game are the agents actively participating in the game and who will experience outcomes based on the play of all players. The **strategies** are all the possible strategic choices available to each player; they can be the same for all players or different for each player. The **payoffs** are the outcomes associated with every possible strategic combination for each player. Any complete description of a game must include these three elements. In the games that we will study in this chapter, we will assume that each player’s goal is to maximize their individual payoff, which is consistent with the rational utility maximizing agent that is the foundation of modern economic theory.

We begin by separating games into two basic types: simultaneous games and sequential games. **Simultaneous games** are games in which players take strategic actions at the same time without knowing what move the other has chosen. A good example of this type of game is the matching coins game where two players each have a coin and choose which side to face up. They then reveal their choices simultaneously, and if they match, one player gets to keep both coins, and if they don’t match, the other player keeps both coins. **Sequential games** are games where players take turns and move consecutively. Checkers, chess, and go are all good examples of sequential games. One player observes the move of the other player and then makes their play and so on.

Games can also be single shot or repeated. **Single-shot** games are played once, and then the game is over. **Repeated games** are simultaneous move games played repeatedly by the same players. A single-shot game might be a game of rock, paper, scissors played once to determine who gets to sit in the front seat of a car. A repeated game might be repeated plays of rock, paper, scissors, with the first player to win five times getting the right to sit in the front seat of a car.

Games can become very complicated when all players do not know all the information about the game. For the purposes of this chapter, we will assume**common knowledge**. Common knowledge is when the players know all about the game—the players, the strategies, and the payoffs—and know that the other players know, that the other players know that they know, and so on ad infinitum. In simpler terms, all participants know everything.

### 17.2 Single Play Games

**Learning Objective 17.2**: Describe normal form games, and identify optimal strategies and equilibrium outcomes in such games.

The most basic of games is the simultaneous, single play game. We can represent such a game with a **payoff matrix**: a table that lists the players of the game, their strategies, and the payoffs associated with every possible strategy combination. We call games that can be represented with a payoff matrix **normal form games**.

Let’s start with an example of a game between two friends, Lena and Sven, who are competing to be the top student in a class. They have a final exam approaching, and they are deciding whether they should be cooperative and share notes or be uncooperative and keep their notes to themselves. They won’t see each other at the end of the day, so they each have to decide whether to leave notes for each other without knowing what the other one has done. If they both share notes, they both will get perfect scores. Their teacher gives a ten-point bonus to the top exam score, but only if there is one exam better than the rest, so if they both get top score, there is no bonus, and they both get 100 on their exams. If they both don’t share, they won’t do as well, and they will both receive a 95 on their exams. However, if one shares and the other doesn’t, the one who shares will not benefit from the other’s notes and will only get a 90, and the one who doesn’t share will benefit from the other’s notes and get the top score and the bonus for a score of 110.

All of these facts are expressed in the payoff matrix in **table 17.1**. Since this is a single-shot, simultaneous game, it is a normal form game, and we can use a payoff matrix to describe it. There are two players: Lena and Sven. There are two strategies available to each player. We will assume common knowledge—they both know all this information about the game, and they know that the other knows it, and they know that the other knows that they know it, and so on.

***Table 17.1** The valedictorian game*

| Note Strategy | Sven’s Payoff | Lena’s Payoff |
|---|---|---|
| Sven shares | 90 | 110 |
| Lena shares | 110 | 90 |
| Neither share | 95 | 95 |
| Both share | 100 | 100 |

The payoff matrix offers a complete description of the game because it lists the three elements: players, strategies, and payoffs.

It is now time to think about individual strategy choices. We will start by examining the difference between dominant and dominated strategies. A **dominant strategy** is a strategy for which the payoffs are always greater than any other strategy no matter what the opponent does. A **dominated strategy** is a strategy for which the payoffs are always lower than any other strategy no matter what the opponent does. Predicting behavior in games is achieved by understanding each rational player’s optimal strategy, the one that leads to the highest payoff. Sometimes the optimal strategy depends on the opponent’s strategy choice, but in the case of a dominant strategy, it does not, and so it follows that a rational player will always play a dominant strategy if one is available to them. It also follows that a rational player will never play a dominated strategy. So we now have our first two principles that can, in certain games, lead to a prediction about the outcome.

Let’s look at the valedictorian game in **table 17.1**. Notice that for Lena, she gets a higher payoff if she doesn’t share her notes no matter what Sven does. If Sven shares his notes, she gets 110 if she doesn’t share rather than 100 if she does. If Sven doesn’t share his notes, she gets 95 if she doesn’t share and 90 if she does. It makes sense then that she will never share her notes. Don’t share is a dominant strategy, so she will play it. Share is a dominated strategy, so she will not play it. The same is true for Sven, as the payoffs in this game happen to be completely symmetrical, though they need not be in games. We can predict that both players will choose to play their dominant strategies and that the outcome of the game will be don’t share, don’t share—Lena chooses don’t share, and Sven chooses don’t share—and they both get 95.

This outcome is known as a**dominant strategy equilibrium ($DSE$)**, an equilibrium where each player plays their dominant strategy. This is a very intuitive equilibrium concept and is the one used in situations where all players have a dominant strategy. Unfortunately, many, or even most, games do not have the feature that every player has a dominant strategy. Let’s examine the DSE in this game. The most striking feature of this outcome is that there is another outcome that both players would voluntarily switch to: share, share. This outcome delivers 100 to each player and is therefore more efficient in the Pareto sense—there is another outcome where you could make one person better off without hurting anyone else. Games with this feature are known as prisoner’s dilemma games—the name comes from a classic game of cops and robbers, but the general usage is for games that have this Pareto-suboptimal feature.

Why do we get this suboptimal result? It comes from the fact that each agent is purely self-interested; all they care about is maximizing their own payoffs, and if they think the other player is going to play share, their best play is to not share. What is particularly interesting about this result is that it overturns the first welfare theorem of economics that says that a competitive equilibrium is Pareto efficient. The difference is the strategic nature of the interactions in the game. Here we have much of the same conditions of a competitive market, but because of the strategic nature of the game, one player’s actions affect the other players’ payoffs.

What if a game lacked dominant strategies? Let’s go back to the example of the last section where you are thinking about which party to attend because you want to meet up with friends. Let’s simplify the example by saying that there are two friends, Malia and Caitlin, who both have been invited to two parties, one sponsored by the college international club and another sponsored by the college debate club. Neither of them has a particular preference about which party they want to go to, but they definitely want to see each other and so want to end up at the same party. They talked earlier in the week, so they know that each is considering the two parties and how much each of them likes the two parties, so there is common knowledge. The problem is that Caitlin’s mobile phone battery has run out of charge, and they can’t communicate. When asked how much they would enjoy the parties, Caitlin and Malia gave similar answers, and we will represent them as payoffs in the payoff matrix in **table 17.2**.

*Table 17.2 The party game, version 1*

|  |  | Malia |  |
|---|---|---|---|
|  |  | International Club (IC) | Debate Club (DC) |
| Caitlin | International Club (IC) | C: 10; M: 10; | C: 2; M: 2 |
| Debate Club (DC) | C: 2; M: 2 | C: 10; M: 10; |  |

This matrix shows Caitlin’s strategies on the left in a column and Malia’s strategies in a row on top. Each of them has exactly two strategies: international club and debate club. For each, their payoffs are shown in the boxes that correspond to each strategy pair. For example, in the boxes for international club, the payoffs are 10 and 10. The first payoff corresponds to Caitlin, and the second corresponds to Malia.

We now have to determine each player’s **best response function**: one player’s optimal strategy choice for every possible strategy choice of the other player. For Caitlin, her best response function is the following:

Play **IC** if Malia plays **IC**.
 Play **DC** if Malia plays **DC**.

For Malia, her best response function looks similar:

Play **IC** if Caitlin plays **IC**.
 Play **DC** if Caitlin plays **DC**.

Since the best response changes for both players depending on the strategy choice of the other player, we know immediately that neither one has a dominant strategy. What then? How do we think about the outcome of the game? The solution concept most commonly used in game theory is the Nash equilibrium concept. A **Nash equilibrium** is an outcome where, given the strategy choices of the other players, no individual player can obtain a higher payoff by altering their strategy choice. An equivalent way to think about Nash equilibrium is that it is an outcome of a game where all players are simultaneously playing a best response to the others’ strategy choices. The equilibrium is intuitive if, when placed in a certain outcome, no player wishes to unilaterally deviate from it, which means equilibrium is achieved—there are no forces within the game that would cause the outcome to change.

In the party game above, there are two outcomes where the best responses correspond: both players choosing IC and both players choosing DC. If Caitlin shows up at the international club party and finds Malia there, she will not want to leave Malia there and go to the debate club party. Similarly, if Malia shows up at the international club party and finds Caitlin there, she will not want to leave Caitlin there and go to the debate club party. So the outcome (IC, IC)—which describes Caitlin’s choice and Malia’s choice—is a Nash equilibrium. The outcome (DC, DC) is also a Nash equilibrium for the same reason.

This example illustrates the strengths and weaknesses of the Nash equilibrium concept. Intuitively, if they show up at the same party, both women would be content, and neither one would want to leave to the other party if the other is staying. However, there is nothing in the Nash equilibrium concept that gives us guidance as to predicting at which party the women will end up. In general, a normal form game can have zero, one, or multiple Nash equilibriums.

Consider this different version of the party game, where Caitlin really doesn’t want to go to the international club party, so much so that she prefers attending the debate club party without Malia to attending the international club party with Malia.

***Table 17.3** The party game, version 2*

|  |  | Malia |  |
|---|---|---|---|
|  |  | International Club (IC) | Debate Club (DC) |
| Caitlin | International Club (IC) | C: 1; M: 10; | C: 1; M: 2 |
| Debate Club (DC) | C: 5; M: 2 | C: 15; M: 10; |  |

Now DC is a dominant strategy for Caitlin. Malia knows Caitlin does not like the international club party and will correctly surmise that she will attend the debate club party no matter what. So both Caitlin and Malia will go to the debate club party, and (DC, DC) is the only Nash equilibrium. In this case, the Nash equilibrium concept is satisfying: it gives a clear prediction of the unique outcome of the game and intuitively makes sense.

Another possibility is a game that has no Nash equilibrium. Consider the game matching pennies. In this game, two players, Ahmed and Naveen, each have a penny. They decide which side of the penny to have facing up and cover the penny until they are both revealed simultaneously. By agreement, if the pennies match, Ahmed gets to keep both, and if the two pennies don’t match, Naveen keeps both. The players, strategies, and payoffs are given in the payoff matrix in **table 17.4**.

***Table 17.4** The matching coin game*

| Round | Ahmed’s Play | Naveen’s Play | Results |
|---|---|---|---|
| Round 1 | Heads | Tails | Ahmed: -1  Naveen: +1 |
| Round 2 | Heads | Heads | Ahmed: +1  Naveen: -1 |
| Round 3 | Tails | Tails | Ahmed: +1  Naveen: -1 |
| Round 4 | Tails | Heads | Ahmed: -1  Naveen: +1 |

Ahmed’s best response function is to play heads if Naveen plays heads and to play tails if Naveen plays tails. Naveen’s best response is to play tails if Ahmed plays heads and to play heads if Ahmed plays tails. As you can clearly see, there is no correspondence of best response functions, no outcome of the game in which a player would want to unilaterally deviate, and thus no Nash equilibrium. The outcome of this game is unpredictable, and no outcome creates contentment for both players.

Finding the Nash equilibrium in normal form games is made relatively easy by following a simple technique that identifies the best response functions on the payoff matrix itself. To do so, simply underline the maximum payoff for a given opponent’s strategy. Consider the example below.

***Table 17.5** The location game, version 1*

|  |  | Pat |  |  |
|---|---|---|---|---|
|  |  | Left | Center | Right |
| Chris | Up | C: 65, P: 44 | C: 29, P: 38 | C: 44, P: 29 |
| Middle | C: 53; P: 41 | C: 35, P: 31 | C: 19, P: 56 |  |
| Down | C: 30, P: 57 | C: 41, P: 63 | C: 72, P: 27 |  |

For Chris, if Pat plays left, the maximum payoff is 65, which comes from playing up, so let’s underline 65. If Pat plays left, Chris should play up. Moving along the columns, we find that Chris should play down if Pat plays center, and Chris should play down again if Pat plays right. Switching perspective, if Chris plays up, Pat gets a maximum payoff from playing left, so we underline Pat’s payoff, 44, in that box. Continuing on, if Chris plays middle, Pat should play right, and if Chris plays down, Pat should play center.

So now that we have identified each player’s best response functions, all that remains is to look for outcomes where the best response functions correspond. Such outcomes are those where both payoffs are underlined. In this game, the two Nash equilibriums are (up, left) and (down, center).

If we change the payoffs in the game to what is shown below, notice that each player has a dominant strategy, as seen by the three underlines all in the row “Down” for Chris and three underlines all in the column “Center” for Pat. Down is always the best strategy choice for Chris no matter what Pat chooses, and center is always the right strategic choice for Pat no matter what Chris chooses.

***Table 17.6** The location game, version 2*

|  |  | Pat |  |  |
|---|---|---|---|---|
|  |  | Left | Center | Right |
| Chris | Up | C: 30, P: 41 | C: 29, P: 44 | C: 44, P: 24 |
| Middle | C: 53; P: 33 | C: 35, P: 56 | C: 19, P: 39 |  |
| Down | C: 65, P: 57 | C: 41, P: 63 | C: 72, P: 27 |  |

Note also that the dominant strategy equilibrium (down, center) also fulfills the requirements of a Nash equilibrium. This will always be true of dominant strategy equilibriums: all dominant strategy equilibriums are Nash equilibriums. From the example above, however, we know the reverse is not true: not all Nash equilibriums are dominant strategy equilibriums. So dominant strategy equilibriums are a subset of Nash equilibriums, or to put it in another way, the Nash equilibrium is a more general concept than the dominant strategy equilibrium.

#### Mixed Strategies

So far we have concentrated on **pure strategies** where a player chooses a particular strategy with complete certainty. We now turn our attention to **mixed strategies**, where a player randomizes across strategies according to a set of probabilities they choose. For an example of a **mixed strategy**, let’s return to the matching pennies game in **table 17.4**.

As was noted before and as we can see by using the underline strategy to illustrate best responses, there is no Nash equilibrium of this game in pure strategies. What about mixed strategies? A mixed strategy is a strategy itself; for example, Ahmed might decide that he will play heads 75 percent of the time and tails 25 percent of the time. What is Naveen’s best response to this strategy? Well if Naveen plays tails with certainty, he will win 75 percent of the time. Ahmed’s best response to Naveen playing tails is to play tails with certainty, so Ahmed’s mixed strategy is not a Nash equilibrium strategy. How about Ahmed choosing a mixed strategy of playing heads and tails, each with a 50 percent chance—simply flipping the coin—can this be a Nash equilibrium strategy? The answer is yes, which is evident when we think of Naveen’s best response to this mixed strategy. Naveen can play either heads or tails with certainty or the same mixed strategy with equal results—he can expect to win half the time. We know that the pure strategies have the best responses as given in the matrix above, so only the mixed strategy is a Nash equilibrium. If Ahmed decides to flip his coin, Naveen’s best response is to flip his too. And if Naveen is flipping his coin, Ahmed’s best response is to do the same.

So this game, which did not have a Nash equilibrium in pure strategies, does have a Nash equilibrium in mixed strategies. Both players randomize over their two strategy choices with probabilities .5 and .5.

### 17.3 Sequential Games

**Learning Objective 17.3**: Describe sequential move games, and explain how they are solved.

There are many situations where players of a game move sequentially. Checkers is such a game: one player moves, the other player observes the move and then responds with their own move, and so on. **Sequential move games** are games where players take turns making their strategic choices: one player observes their opponent’s choice prior to making their own strategic choice. We describe these games by drawing a**game tree**, a diagram that describes the players, their turns, their choices at every turn, and the payoffs for every possible set of strategy choices. We have another name for this description of sequential games: **extensive form games**.

Consider a game where two Indian food carts located next to each other are competing for many of the same customers for their tikka masala. The first cart, called Ashok’s, opens first and sets its price; the second cart, called Tridip’s, opens second and sets its price after observing the price set by Ashok’s. To keep it simple, let’s suppose there are three prices possible for both carts: high, medium, low.

The extensive form, or game tree, representation of this game is given in **f****igure 17.1**. The game tree describes all the principal elements of the game: the players, the strategies, and the payoffs. The players are described at each decision node of the game, each place where a player might potentially have to choose a strategy. From each node, branches extend, representing the strategy choices of a player. At the end of the final set of branches are the payoffs for every possible outcome of the game. This is the complete description of the game. There are also subgames within the full game. Subgames are all the subsequent strategy decisions that follow from one particular node.

> [Рисунок] **Figure 17.1** The curry pricing game (https://open.oregonstate.education/app/uploads/sites/203/2022/07/1731Artboard-1.svg)

In this game, Ashok’s is at the first decision node, so they get to move first. Tridip’s is at the second set of decision nodes, so they move second. How will the game resolve itself? To determine the outcome, it is necessary to use backward induction: to start at the last play of the game and determine what the player with the last turn of the game will do in each situation and then, given this deduction, determine what the payer with the second-to-last turn will do at that turn and continue this way until the first turn is reached. Using backward induction leads to the subgame perfect Nash equilibrium of the game. The **subgame perfect Nash equilibrium ($SPNE$)** is the solution in which every player, at every turn of the game, is playing an individually optimal strategy.

For the curry pricing game illustrated in **figure 17.1**, the $SPNE$ is found by first determining what Tridip’s will do for each possible play by Ashok’s. Tridip’s is only concerned with his payoffs in red and will play medium if Ashok’s plays high and thus will get 410, will play low if Ashok’s plays medium and will get 360, and will play low if Ashok’s plays low and will get 310. Because of common knowledge, Ashok’s knows this as well and so has only three possible outcomes. Ashok’s knows that if they play high, Tridip’s will play medium, and Ashok’s will get 340; if they play medium, Tridip’s will play low, and Ashok’s will get 210; and if they play low, Tridip’s will play low, and Ashok’s will get 320. Since 340 is the best of the possible outcomes, Ashok’s will pick high. Since Ashok’s picks high, Tridip’s will pick medium, and the game ends.

Backward induction will always lead to the $SPNE$ of a sequential game.

#### Credible and Non-credible Threats

Let’s consider a famous game where there is an established “incumbent” firm in a market and another entrepreneur who is thinking of entering the market and competing with the incumbent, who we will call the “potential entrant.” Suppose, for example, that there is just one pizza restaurant in a commercial district just off a university campus that sells pizza slices to the students of the university, let’s call it Gino’s. Since they face no direct competition, they can sell a slice of pizza for $3, and they make $400 a day in revenue. But there is a pizza maker named Vito who is considering entering the market by setting up a pizza shop in an empty storefront just down the street from Gino’s. When facing the potential arrival of Vito’s pizza restaurant, Gino has two choices: accommodate Vito by keeping prices higher (say, $2) or fighting Vito by selling his slices below cost in the hope of preventing Vito from opening. The game and the payoffs are given below in the normal form game in **Table 17.7**.

In **Table 17.8**, we see that if we follow the underlining strategy to identify the best responses, this game has two Nash equilibriums: (accommodate, enter) and (fight, don’t enter). Note that for Gino, both accommodate and fight result in the same payoff if Vito chooses don’t enter, so we underline both—either one is equally a best response.

***Table 17.7** The market entry game*

|  |  | Vito’s (Potential Entrant) |  |
|---|---|---|---|
|  |  | Enter | Don’t Enter |
| Gino’s  (Incumbent) | Accommodate | G: 200; V: 300; | G: 400; V: 0 |
| Fight | G: 100; M: 200 | G: 400; M: 0; |  |

***Table 17.8** Nash equilibrium in the market entry game*

|  |  | Vito’s (Potential Entrant) |  |
|---|---|---|---|
|  |  | Enter | Don’t Enter |
| Gino’s  (Incumbent) | Accommodate | G: 200; V: 300; | G: 400; V: 0 |
| Fight | G: 100; M: 200 | G: 400; M: 0; |  |

But there is something unsatisfying about the second Nash equilibrium—since this is a simultaneous game, both players are picking their strategies simultaneously. Thus Gino is picking fight if Vito does not enter, and so Vito’s best choice is not to enter. But would Vito really believe that Gino would fight if he entered? Probably not. We call this a non-credible threat: a strategic choice to dissuade a rival that is against the best interest of the player and therefore not rational.

A better description of this game is therefore a sequential one, where Vito first chooses to open a pizza restaurant and Gino has to decide how to respond.

> [Рисунок] **Figure 17.2** The sequential market entry game (https://open.oregonstate.education/app/uploads/sites/203/2022/07/1733Artboard-1.svg)

In this version of the game, if Vito decides not to enter, the game ends, and the payoffs are $0 for Vito and $400 for Gino. If Vito decides to enter, then Gino can either fight and get $−100 or accommodate and get $200. Clearly, the only individually rational thing for Gino to do if Vito enters is to accommodate, and since Vito knows this, he will enter.

> [Рисунок] **Figure 17.3** The squential market entry game $SPNE$ (https://open.oregonstate.education/app/uploads/sites/203/2022/07/1733bArtboard-1.svg)

The $SPNE$ of this game is (enter, accommodate). What this version of the game does is eliminate the equilibrium based on a non-credible threat. Vito knows that if he decides to open up a pizza shop, it is irrational for Gino to fight because Gino will make himself worse off. Since Vito knows that Gino will accommodate, the best decision for Vito is to open his restaurant.

### 17.4 Repeated Games

**Learning Objective 17.4**: Describe repeated games and the difference between finitely repeated games and infinitely repeated games and their equilibrium.

Any game can be played more than once to create a larger game. For example, the game rock, paper, scissors, where two players simultaneously use their hands to form the shape of a rock, a piece of paper, or scissors can be played just once or can be repeated multiple times—for example, playing “best of three,” where the winner is the first player to win two rounds of the game. This is a normal form game in each round but a larger game when taken as a whole. This raises the possibility that a larger strategy could be employed—for example, one contingent on the choice of the opponent in the last round.

Let’s return to the valedictorian game from section 17.2. Recall that this game was a prisoner’s dilemma; because of individual incentives, they find themselves in a collectively suboptimal outcome. In other words, there is an outcome that they both prefer, but they fail to reach it because of the individual strategic incentive to try to do better for themselves. But if the same game was repeated more than once over the course of the school year, it is quite reasonable to ask if such repetition would lead the players to a different outcome. If the players know they will face the same situation again, will they be more inclined to cooperate and reach a mutually beneficial outcome?

#### Finitely Repeated Games

If we played the valedictorian game twice, then the strategies for each player would entail their strategy choices for each round of the game. In other words, a “strategy” for a repeated game is the complete set of strategic choices for every round of the game. So let’s ask if playing the valedictorian game twice would alter the outcome in an individual round. Suppose, for example, the two talked before the game and acknowledged that they would both be better off cooperating and sharing. In the repeated game, is cooperation ever a Nash equilibrium strategy?

To answer this question, we have to think about how to solve the game. Since this game is repeated a finite number of times, in our case two, it has a final round, and similar to a sequential game, the appropriate method of solving the game is through backward induction to find the subgame perfect Nash equilibrium. In repeated games, at each round, the subsequent games are a subgame of the overall game. So in our case, the second and final round of the game is a subgame. So to solve the game, we have to first think about the outcome of the final round. Well, this final play of the game is the simple normal form game we have already solved, a single-shot, simultaneous play game with one Nash equilibrium: (don’t share, don’t share).

Now that we know what will happen in the final round of the game, we have to ask ourselves, What is the Nash equilibrium strategy in the first round of play? Since they both know that in the final round of play, the only outcome is for both to not share, they also know that there is no reason to share in the first round either. Why? Well, even if they agree to share, when push comes to shove, not sharing is better individually, and since not sharing is going to happen in the final round anyway, there is no way to create an incentive to share in the first round through a final round punishment mechanism. In essence, after the last period is revealed to be a single-shot prisoner’s dilemma game, the second-to-last period becomes a single-shot prisoner’s dilemma game as well because there is nothing in the last round that can alter the incentives in the second-to-last round, so the game is identical.

In fact, as long as there is a final round, it doesn’t matter how many times we repeat this game; because of backward induction, it simply becomes a series of single-shot games with the Nash equilibrium strategies being played every time.

#### Infinitely Repeated Games

Things change when normal form games are repeated infinitely because there is no final round, and thus backward induction does not work; there is nowhere to work backward from. This aspect of the games allows space for reward and punishment strategies that might create incentives under which cooperation becomes a Nash equilibrium.

To see this, let’s alter the scenario of our valedictorian game. Suppose that Lena and Sven are now adults in the workplace, and they work together in a company where their pay is based partly on their performance on a monthly aptitude test. For simplicity, we’ll assume that their payoffs are the same as in the valedictorian game, but this time, they represent cash bonuses. The key here is that they foresee working together for as long as they can imagine. In other words, they each perceive the possibility that they will keep playing this game for an indeterminate amount of time—there is no determined last round of the game and therefore no way to use backward induction to solve it. Players have to look ahead to determine the optimal strategies.

So what would a strategy to induce cooperation look like? Suppose Lena says to Sven, “I will share with you as long as you share with me, but as soon as you don’t share, I will stop sharing with you forever”—let’s call this the “cooperate” strategy. Sven, in response, says, “OK, I will do the same. I will share with you until such time as you don’t share, and then I’ll stop sharing altogether.” We must then ask, Is the act of both players playing these strategies a Nash equilibrium?

To answer this question, we have to figure out the best response to the strategy: Is it to play the same strategy, or is there a better strategy to play in response? To determine the answer to this question, let’s think about playing the same strategy and alternate strategies and their payoffs.

If Lena claims she will play the cooperate strategy, what is Sven’s outcome if he plays the cooperate strategy in response? Well, in the first period, Sven will get 100 because they both share, and since they both shared in period one, they will both share in period two, and so Sven will get 100, and it will continue like this forever. To put a present-day value on future earnings, we discount, so Sven’s earnings stream **(the payoff from a cooperate** **strategy**) looks as follows:

$100 + 100 \times d + 100 \times d^2 + 100 \times d^3 + 100 \times d^4+...$

What is the payoff from not cooperating? Well, in the period in which Sven decides not to share, Lena will still be sharing, and so Sven will get 110, but then after that, Lena will not share, and Sven knows this, so he will not share as well, and he will therefore get 95 for every round after. Let’s call this strategy “deviate.” Thus his earning stream (the **payoff from a deviate strategy**) looks like the following:

$110 + 95 \times d + 95 \times d^2 + 95 \times d^3 + 95 \times d^4+...$

Note that we are only comparing the two strategies from the moment Sven decides to deviate, as the two payoff streams are identical up to that point and therefore cancel themselves out.

Is to cooperate the best response to the cooperate strategy? Yes, if

$100 + 100 \times d + 100 \times d^2 + 100 \times d^3 + 100 \times d^4+...$

$\gt 110 + 95 \times d + 95 \times d^2 + 95 \times d^3 + 95 \times d^4+...$.

Rearranging, we get:

$5(d+d^2+d^3+d^4+...)\gt 10$

This says that cooperation is better as long as the extra five points a cooperating player gets for every subsequent period after the first is better than the extra ten the deviating player gets in the first period. To determine if this is true, we have to use the result that

$d+d^2+d^3+d^4+...=\frac{d}{1 − 4}$.

So $5(\frac{d}{1-d})\gt 10$, or

$5d \gt 10(1-d)$
 $15d \gt 10$
 $d \gt \frac{2}{3}$.

You can think of $d$ as a measure of how much the players care about future payoffs, and so this says that as long as they care enough about the future payoffs, they will cooperate. In other words, if $d \gt \frac{2}{3}$, then playing cooperate is a best response to the other player playing cooperate and vice versa: the strategy pair (cooperate, cooperate) is a Nash equilibrium for the infinitely repeated game.

This type of strategy has a name in economics: a **trigger strategy**. A trigger strategy is one where cooperative play continues until an opponent deviates and then ceases permanently or for a specified number of periods. An alternate strategy is the **tit-for-tat strategy**, where a player simply plays the same strategy their opponent played in the previous round. Tit-for-tat strategies can also be a Nash equilibrium, and in fact, in infinitely repeated games where there are often many Nash equilibriums, the trigger strategy identified above is just one of many.

### 17.5 Policy Example
 **Do We Need to Regulate Banks to Save Them from Themselves?**

**Learning Objective 17.5**: Explain how game theory can be used to understand the banking collapse of 2008.

In the mid-2000s, banks in the United States found themselves struggling to satisfy a tremendous demand for mortgages from the market for mortgage-backed securities: securities that were created from bundles of residential or commercial mortgages. This, along with the low-interest rate policy of the Federal Reserve, led to a tremendous housing boom in the United States that evolved into a speculative investment bubble. The bursting of this bubble led to the housing market crash and, in 2008, to a banking crisis: the failure of major banking institutions and the unprecedented government bailout of banks. These twin crises led to the worst recession since the Great Depression.

Interestingly, this banking crisis came relatively soon after a series of reforms of banking regulations in the United States that gave banks much more freedom in their operations. Most notably was the 1999 repeal of the provisions of the Glass-Steagall Act, enacted after the beginning of the Great Depression in 1933, which prohibited commercial banks from engaging in investment activities.

Part of the argument at the time of the repeal was that banks should be allowed to innovate and be more flexible, which would benefit consumers. The rationale was that increased competition and the discipline of the market would inhibit excessive risk-taking, so stringent government regulation was no longer necessary. But the discipline of the market assumes that rewards are absolute, meaning that returns are not based on relative performance or that the environment is not strategic. Is this an accurate description of modern banking? Probably not.

In everything from stock prices to CEO pay, relative performance matters, and if one bank were to rely on a low-risk strategy while others were engaging in higher risk–higher reward strategies, both the company’s stock price and the compensation of the CEO might suffer. We can describe this in a very simplified model where there are two banks, and they can engage in either low-risk or high-risk strategies. This scenario is described in **table 17.9**, where we have two players, Big Bank and Huge Bank; the two strategies for each; and the payoffs (in millions):

***Table 17.9** The risky banking game*

|  |  | Huge Bank |  |
|---|---|---|---|
|  |  | Low-Risk | High-Risk |
| Big Bank | Low-Risk | B: 30; H: 30; | B: 22; H: 45; |
| High-Risk | B: 45; H: 22; | B: 25; H: 25; |  |

We can see from the normal form game that both banks have dominant strategies: high risk. This is because the rewards are relative. Being a high-risk bank when your competitor is a low-risk bank brings a big reward; the relatively high returns are compounded by the reward from the stock market. In the end, both banks end up choosing high risk and are in a worse outcome than if they had chosen a low-risk strategy because of the increased likelihood of negative events from the strategy. Astute observers will recognize this game as a prisoner’s dilemma, where behavior based on the individual self-interest of the banks leads them to a second-best outcome. If you include the cost to society of bailing out high-risk banks when they fail, the second-best outcome is that much worse.

Can policy correct the situation and lead to a mutually beneficial outcome? The answer in this case is a **resounding yes**. If policy makers take away the ability of the banks to engage in high-risk strategies, the bad equilibrium will disappear, and only the low-risk, low-risk outcome will remain. The banks are better off, and because the adverse effects of high-risk strategies going bad are taken away, society benefits as well.

### Exploring the Policy Question

1. Why do you think that banks were so willing to engage in risky bets in the early 2000s?
2. Do you think that government regulation restricting their strategy choices is appropriate in cases where society has to pay for risky bets gone bad?

**[REVIEW: TOPICS AND RELATED LEARNING OUTCOMES]**

#### 17.1 What Is Game Theory?

**Learning Objective 17.1**: Describe game theory and the types of situations it describes.

#### 17.2 Single Play Games

**Learning Objective 17.2**: Describe normal form games, and identify optimal strategies and equilibrium outcomes in such games.

#### 17.3 Sequential Games

**Learning Objective 17.3**: Describe sequential move games, and explain how they are solved.

#### 17.4 Repeated Games

**Learning Objective 17.4**: Describe repeated games and the difference between finitely repeated games and infinitely repeated games and their equilibrium.

#### 17.5 Policy Example
 **Do We Need to Regulate Banks to Save Them from Themselves?**

**Learning Objective 17.5**: Explain how game theory can be used to understand the banking collapse of 2008.

**[learn: key topics]**

#### Terms

Strategic interactions

Interactions in which agents must anticipate the actions of others when making decisions. Game theory is uesd to model them.

Game theory

The study of strategic interactions among economic agents. Any complete description of a game must include the following three elements:

- Players
   The agents actively participating in a game and who will experience outcomes based on the play of all players.
- Strategies
   All the possible strategic choices available to each player; can be the same for all players, the same for some players, or different for each player.
- Payoffs
   The outcomes associated with every possible strategic combination between players.

Non-cooperative games

Games in which the players are not able to negotiate and make binding agreements within the game, i.e., most competitive sports.

Simultaneous games

Games in which players take strategic actions at the same time without knowing what move the other has chosen, i.e., tag, rock paper scissors, real-time strategy games.

Sequential games

Games where players take turns and move consecutively, i.e., checkers, chess, a turn-based RPG.

Single-shot games

Games that are played once and then are over, i.e., rock paper scissors to determine who gets to sit in the front seat of the car.

Repeated games

Simlutaneous move games played repeatedly by the same players, i.e., rock paper scissors, best out of five.

Common knowledge

All participants are aware of all components in a game, and are also aware that all participants are aware.

Payoff matrix

A table that lists the players of the game, their strategies, and the payoffs associated with every possible strategy combination.

Normal form games

Games that can be represented with a payoff matrix.

Dominant strategy

A strategy for which the payoffs are always greater than any other strategy no matter what the opponent does.

Dominated strategy

A strategy for which the payoffs are always lower than any other strategy no matter what the opponent does.

Dominant strategy equilibrium (DSE)

An equilibrium in which each player plays their dominant strategy.

Best response function

A player’s optimal strategy choice for every possible strategy choice of the other player.

Nash equilibrium

An outcome where, given the strategy choices of the other players, no individual player can obtain a higher payoff by altering their strategy choice.

Pure strategies

A strategy a player selects with complete certainty.

Mixed strategies

A player randomizes strategies according to a set of probabilities that they choose.

Sequential move games

Games where players take turns making their strategic choices. Generally modeled by a game tree.

Game tree

A diagram that describes the players, their turns, their potential strategies for each turn, and the payoffs for every possible set of strateies.

Extensive form games

Another name for sequential move games.

Subgame perfect Nash equilibrium (SPNE)

The solution in which every player, at every turn of teh game, is playing an individually optimal strategy.

Trigger strategy

A strategy where cooperative play continues until an opponent deviates and then ceases permanently or for a specified number of period. In infinitely repeated games, where there are often many Nash equilibriums, the trigger strategy is just one of many.

Tit-for-tat strategy

A player simply plays the same strategy their opponent played in the previous round–can be considered a Nash equilibrium.

#### Tables and Figures

The valedictorian game

*The valedictorian game*

| Note Strategy | Sven’s Payoff | Lena’s Payoff |
|---|---|---|
| Sven shares | 90 | 110 |
| Lena shares | 110 | 90 |
| Neither share | 95 | 95 |
| Both share | 100 | 100 |

The party game, version 1

*Figure 17.2.2 The party game, version 1*

|  |  | Malia |  |
|---|---|---|---|
|  |  | International Club (IC) | Debate Club (DC) |
| Caitlin | International Club (IC) | C: 10; M: 10; | C: 2; M: 2 |
| Debate Club (DC) | C: 2; M: 2 | C: 10; M: 10; |  |

The party game, version 2

***Figure 17.2.3** The party game, version 2*

|  |  | Malia |  |
|---|---|---|---|
|  |  | International Club (IC) | Debate Club (DC) |
| Caitlin | International Club (IC) | C: 1; M: 10; | C: 1; M: 2 |
| Debate Club (DC) | C: 5; M: 2 | C: 15; M: 10; |  |

The matching pennies game

***Table 17.4** The matching coin game*

| Round | Ahmed’s Play | Naveen’s Play | Results |
|---|---|---|---|
| Round 1 | Heads | Tails | Ahmed: -1  Naveen: +1 |
| Round 2 | Heads | Heads | Ahmed: +1  Naveen: -1 |
| Round 3 | Tails | Tails | Ahmed: +1  Naveen: -1 |
| Round 4 | Tails | Heads | Ahmed: -1  Naveen: +1 |

The curry pricing game

> [Рисунок] Figure 17.1 The curry pricing game (https://open.oregonstate.education/app/uploads/sites/203/2022/07/1731Artboard-1.svg)

The market entry game

***Table 17.8** Nash equilibrium in the market entry game*

|  |  | Vito’s (Potential Entrant) |  |
|---|---|---|---|
|  |  | Enter | Don’t Enter |
| Gino’s  (Incumbent) | Accommodate | G: 200; V: 300; | G: 400; V: 0 |
| Fight | G: 100; M: 200 | G: 400; M: 0; |  |

The sequential market entry game

> [Рисунок] Figure 17.2 The market entry game (https://open.oregonstate.education/app/uploads/sites/203/2022/07/1733Artboard-1.svg)

> [Рисунок] Figure 17.3 The squential market entry game SPNE (https://open.oregonstate.education/app/uploads/sites/203/2022/07/1733bArtboard-1.svg)

The risky banking game

***Table 17.9** The risky banking game*

|  |  | Huge Bank |  |
|---|---|---|---|
|  |  | Low-Risk | High-Risk |
| Big Bank | Low-Risk | B: 30; H: 30; | B: 22; H: 45; |
| High-Risk | B: 45; H: 22; | B: 25; H: 25; |  |

#### Equations

Payoff from a cooperate strategy

$100 + 100 \times d + 100 \times d^2 + 100 \times d^3 + 100 \times d^4+...$

Payoff from a deviate strategy

$110 + 95 \times d + 95 \times d^2 + 95 \times d^3 + 95 \times d^4+...$

##### Comparing the Two

Is to cooperate the best response to the cooperate strategy? Yes, if

$100 + 100 \times d + 100 \times d^2 + 100 \times d^3 + 100 \times d^4+...$
 $\gt 110 + 95 \times d + 95 \times d^2 + 95 \times d^3 + 95 \times d^4+...$

Which can be rearranged into:

$5(d+d^2+d^3+d^4+...)\gt 10$

When applied to the valedictorian game, the equation says cooperation is better that as long as the extra five points a cooperating player gets for every subsequent period after the first is better than the extra ten the deviating player gets in the first period. We can test that with the following equation:

$d+d^2+d^3+d^4+...=\frac{d}{1 − 4}$

Thus

$5(\frac{d}{1-d})\gt 10$, or
 $5d \gt 10(1-d)$
 $15d \gt 10$
 $d \gt \frac{2}{3}$

The variable $d$ can be thought of as a measure of how much the players care about future payoffs. With $d\gt\frac{2}{3}$, we can assume that the players will cooperate due to their concern over future outcomes.

### Media Attributions

- 1731Artboard-1 © Patrick M. Emerson is licensed under a
   CC BY-NC-SA (Attribution NonCommercial ShareAlike)
   license
- 1733Artboard-1 © Patrick M. Emerson is licensed under a
   CC BY-NC-SA (Attribution NonCommercial ShareAlike)
   license
- 1733bArtboard-1 © Patrick M. Emerson is licensed under a
   CC BY-NC-SA (Attribution NonCommercial ShareAlike)
   license
