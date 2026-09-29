# 02. Utility

> Источник: Patrick M. Emerson, *Intermediate Microeconomics*, Oregon State University, 2019. https://open.oregonstate.education/intermediatemicroeconomics/chapter/module-2/
> Лицензия: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/) — только некоммерческое использование, с указанием автора, производные — под той же лицензией. Текст сконвертирован в markdown без изменений по смыслу; формулы — LaTeX в `$...$`; рисунки — ссылками.

> [Рисунок] “Fill ‘Er Up” by derekbruff is licensed under CC BY-NC 2.0 (https://open.oregonstate.education/app/uploads/sites/203/2022/06/zero-emission-1024x683-1.jpg)

### The Policy Question
 **Is a tax credit on hybrid car purchases the government’s best choice to reduce fuel consumption and carbon emissions?**

US residents and the government are concerned about the dependence on imported foreign oil and the release of carbon into the atmosphere. In 2005, Congress passed a law to provide consumers with tax credits toward the purchase of electric and hybrid cars.

This tax credit may seem like a good policy choice, but it is costly because it directly lowers the amount of revenue the US government collects. Are there more effective approaches to reducing dependency on fossil fuels and carbon emissions? How do we decide which policy is best? To answer this question, policymakers need to predict with some accuracy how consumers will respond to this tax policy before these policymakers spend millions of federal dollars.

We can apply the concept of *utility* to this policy question. In this chapter, we will study utility and utility functions. We will then be able to use an appropriate utility function to derive indifference curves that describe our policy question.

### Exploring the Policy Question

1. Suppose that the tax credit to subsidize hybrid car purchases is wildly successful and doubles the average fuel economy of all cars on US roads—a result that is clearly not realistic but useful for our subsequent discussions. What do you think would happen to the fuel consumption of all US motorists? Should the government expect fuel consumption and carbon emissions from cars to decrease by half in response? Why or why not?

**[LEARNING OBJECTIVES]**

#### 2.1 Utility Functions

**Learning Objective 2.1**: Describe a utility function.

#### 2.2 Utility Functions and Typical Preferences

**Learning Objective 2.2**: Identify utility functions based on the typical preferences they represent.

#### 2.3 Relating Utility Functions and Indifference Curve Maps

**Learning Objective 2.3**: Explain how to derive an indifference curve from a utility function.

#### 2.4 Finding Marginal Utility and Marginal Rate of Substitution

**Learning Objective 2.4**: Derive marginal utility and MRS for typical utility functions.

#### 2.5 Policy Example
 Is a Tax Credit on Hybrid Car Purchases the Government’s Best Choice?

**Learning Objective 2.5**: The Hybrid Tax Credit and customer utility

### 2.1 Utility Functions

**Learning Objective 2.1:** Describe a utility function.

Our preferences allow us to make comparisons between different consumption bundles and choose the preferred bundles. We could, for example, determine the rank ordering of a whole set of bundles based on our preferences. A**utility function** is a mathematical function that ranks bundles of consumption goods by assigning a number to each, where larger numbers indicate preferred bundles. Utility functions have the properties we identified in [chapter 1](http://open.oregonstate.education/intermediatemicroeconomics/module-1#section1-1) regarding preferences. That is, they are able to order bundles, they are complete and transitive, more is preferred to less, and in relevant cases, mixed bundles are better.

The number that the utility function assigns to a specific bundle is known as **utility**, the satisfaction a consumer gets from a specific bundle. The utility number for each bundle does not mean anything in absolute terms; there is no uniform scale against which we measure satisfaction. Its only purpose is in relative terms: we can use utility to determine which bundles are preferred to others.

If the utility from bundle $A$ is higher than the utility from bundle $B$, it is equivalent to saying that a consumer prefers bundle $A$ to bundle $B$. Utility functions, therefore, rank consumer preferences by assigning a number to each bundle. We can use a utility function to draw the indifference curve maps described in [chapter 1](http://open.oregonstate.education/intermediatemicroeconomics/module-1#section1-2). Since all bundles on the same indifference curve provide the same satisfaction and therefore none is *preferred*, each bundle has the same utility. We can therefore draw an indifference curve by determining all the bundles that return the same number from the utility function.

Economists say that utility functions are **ordinal** rather than**cardinal**. Ordinal means that utility functions only rank bundles—they only indicate which one is better, not how much better it is than another bundle. Suppose, for example, that one utility function indicates that bundle$A$ returns ten **utils** and bundle$B$twenty utils. We do not say that bundle $B$ is twice as good, or ten utils better, only that the consumer prefers bundle $B$. For example, suppose a friend entered a race and told you she came in third. This information is **ordinal**: You know she was faster than the fourth-place finisher and slower than the second-place finisher. You only know the order in which runners finished. The *individual times* are **cardinal**: if the first-place finisher ran the race in exactly one hour and your friend finished in one hour and six minutes, you know your friend was exactly 10 percent slower than the fastest runner. Because utility functions are ordinal, many different utility functions can represent the same preferences. This is true as long as the ordering is preserved.

Take, for example, the utility function $U$ that describes preferences over bundles of goods $A$ and $B$: $U(A,B)$. We can apply any **positive monotonic transformation** to this function (which means, essentially, that we do not change the ordering), and the new function we have created will represent the same preferences. For example, we could multiply a positive constant, $\alpha$, or add a positive or a negative constant, $\beta$. So $\alpha U(A,B)+ \beta$ represents exactly the same preferences as $U(A,B)$ because it will order the bundles in exactly the same way. This fact is quite useful because sometimes applying a positive monotonic transformation of a utility function makes it easier to solve problems.

### 2.2 Utility Functions and Typical Preferences

**Learning Objective 2.2:** Identify utility functions based on the typical preferences they represent.

Consider bundles of apples, $A$, and bananas, $B$. A utility function that describes Isaac’s preferences for bundles of apples and bananas is the function $U(A,B)$. But what are Isaac’s particular preferences for bundles of apples and bananas? Suppose that Isaac has fairly standard preferences for apples and bananas that lead to our typical indifference curves: he prefers more to less, and he likes variety. A utility function that represents these preferences might be

$U(A,B) = AB$

If apples and bananas are perfect complements in Isaac’s preferences, the utility function would look something like this:

$U(A,B) = MIN[A,B]$

where the $MIN$ function simply assigns the smaller of the two numbers as the function’s value.

If apples and bananas are perfect substitutes, the utility function is an additive and would look something like this:

$U(A,B) = A + B$

**Cobb-Douglas utility functions** are commonly used in economics for two reasons:

1. They represent
   standard preferences
   , such as
   more is better
   and
   preference for variety
   .
2. They are very flexible and can be adjusted to fit real-world data very easily.

Cobb-Douglas utility functions have this form:

$U(A,B) = A^\alpha B^\beta$

Because positive monotonic transformations represent the same preferences, one such transformation can be used to set $\alpha + \beta = 1$, which later we will see is a convenient condition that simplifies some math in the consumer choice problem.

Another way to transform the utility function in a useful way is to take the natural log of the function, which creates a new function that looks like this:

$U(A,B) = \alpha ln(A) + \beta ln(B)$

To derive this equation, simply apply the rules of natural logs. It is important to keep in mind the level of abstraction here. We typically cannot make specific utility functions that precisely describe individual preferences. Probably none of us could describe our own preferences with a single equation. But as long as consumers in general have preferences that follow our basic assumptions, we can do a pretty good job finding utility functions that match real-world consumption data. We will see evidence of this later in the course.

***Table 2.1** Types of preferences and the utility functions that represent them*

| **Preferences** | **Utility function** | **Type of utility function** |
|---|---|---|
| Love of variety or “well behaved” | $U(A,B) = AB$ | Cobb-Douglas |
| Love of variety or “well behaved” | $U(A,B) = A^\alpha B^\beta$ | Cobb-Douglas |
| Love of variety or “well behaved” | $U(A,B) = \alpha ln(A) + \beta ln(B)$ | Natural log Cobb-Douglas |
| Perfect complements | $U(A,B) = MIN[A,B]$ | Min function |
| Perfect substitutes | $U(A,B) = A + B$ | Additive |

### 2.3 Relating Utility Functions and Indifference Curve Maps

**Learning Objective 2.3**: Explain how to derive an indifference curve from a utility function.

Indifference curves and utility functions are directly related. In fact, since indifference curves represent preferences graphically and utility functions represent preferences mathematically, it follows that indifference curves can be derived from utility functions.

In**univariate functions**, the dependent variable is plotted on the vertical axis, and the independent variable is plotted on the horizontal axis, like the graph of $y=f(x)$. In contrast, graphs of **bivariate functions** are three-dimensional, like $U=U(A,B)$. **Figure 2.1** shows a graph of $U=A^\frac{1}{2}B^\frac{1}{2}$. Three-dimensional graphs are useful for understanding how utility increases with the increased consumption of both A and B.

> [Рисунок] **Figure 2.1**$U=A^\frac{1}{2}B^\frac{1}{2}$ (https://open.oregonstate.education/app/uploads/sites/203/2022/07/fig2.1-768x768-1-300x300.png)

**Figure 2.1** clearly shows the assumption that consumers have a preference for variety. Each bundle, which contains a specific amount of $A$ and $B$, represents a point on the surface. The vertical height of the surface represents the level of utility. By increasing both $A$ and $B$, a consumer can reach higher points on the surface.

So where do indifference curves come from? Recall that an indifference curve is a collection of all bundles that a consumer is indifferent about with respect to which one to consume. Mathematically, this is equivalent to saying all bundles, when put into the utility function, return the same functional value. So if we set a value for utility, $Ū$, and find all the bundles of $A$ and $B$ that generate that value, we will define an indifference curve. Notice that this is equivalent to finding all the bundles that get the consumer to the same height on the three-dimensional surface in **figure 2.1**.

Indifference curves are a representation of elevation (utility level) on a flat surface. In this way, they are analogous to a contour line on a topographical map. By taking the three-dimensional graph back to two-dimensional space—**the A, B space**—we can show the contour lines / indifference curves that represent different elevations or utility levels. From the graph in **figure 2.1**, you can already see how this utility function yields indifference curves that are “bowed-in” or concave to the origin.

So indifference curves follow directly from utility functions and are a useful way to represent utility functions in a two-dimensional graph.

### 2.4 Finding Marginal Utility and Marginal Rate of Substitution

**Learning Objective 2.4**: Derive marginal utility and MRS for typical utility functions.

**Marginal utility $(MU)$** is the additional utility a consumer receives from consuming one additional unit of a good. Mathematically, we express this as

$MU_{A}=\frac{\Delta U}{\Delta A}$

or the change in utility from a change in the amount of $A$ consumed, where Δ represents a change in the value of the item, so

$MU_{A}=\frac{\Delta U}{\Delta A}=\frac{U (A+\Delta A,B)-U(A,B)}{\Delta A}$

Note that when we are examining the marginal utility of the consumption of $A$, we hold $B$ constant.

Using calculus, the marginal utility is the same as the partial derivative of the utility function with respect to $A$:

$MU_{A}=\frac{\partial U(A,B)}{\partial A}$

Consider a consumer who sits down to eat a meal of salad and pizza. Suppose that we hold the amount of salad constant—one side salad with a dinner, for example. Now let’s increase the slices of pizza; suppose with one slice, utility is ten; with two, it is eighteen; with three, it is twenty-four; and with four, it is twenty-eight. Let’s plot these numbers on a graph that has utility on the vertical axis and pizza on the horizontal axis (**table 2.2** and **figure 2.2**).

***Table 2.2** Diminishing marginal utility*

| **Pizza slices** | **Utility** | **Marginal utility** |
|---|---|---|
| 1 | 10 |  |
| 2 | 18 | 8 |
| 3 | 24 | 6 |
| 4 | 28 | 4 |

> [Рисунок] **Figure 2.2** Diminishing marginal utility (https://open.oregonstate.education/app/uploads/sites/203/2022/07/fig2.2-1-300x183.png)

From the positive slope of the graph, we can see the increase in utility from additional slices of pizza. From the concave shape of the graph, we can see another common phenomenon: the additional utility the consumer receives from each additional slice of pizza decreases with the number of slices consumed.

The fact that the additional utility gets smaller with each additional slice of pizza is called the principle of **diminishing marginal utility**. This principle applies to well-behaved preferences where mixed bundles are preferred.

[**Marginal rate of substitution (MRS)**](http://open.oregonstate.education/intermediatemicroeconomics/chapter/module-1#section1-4) is the amount of one good a consumer is willing to give up to get one more unit of another good. This is why it is the same thing as the *slope of the indifference curve*—since we keep satisfaction level constant, we stay on the same indifference curve, just moving along it as we trade one good for another. How much of one you are willing to trade for one more of another depends on the marginal utility of each.

Using our previous example, if by consuming one more side salad, your utility goes up by ten, then at a current consumption of four slices of pizza, you could give up two slices of pizza and go from twenty-eight to eighteen utils. Ten more utils from salad and ten fewer utils by giving up two slices of pizza leave overall utility unchanged—so we must still be on the same indifference curve. As you move along the indifference curve, you must be riding the slope—that is, you must be giving up the good on the vertical axis for more of the good on the horizontal axis, which yields a negative rise over a positive run.

We can go directly from marginal utility to$MRS$ by recognizing the connection between the two concepts. In our case, for the utility function $U=U(A,B)$, $MRS$ is represented as

$MRS=-\frac{MU_{A}}{MU_{B}}$

Note that when we substitute, we can simplify the equation:

$MRS=-\frac{MU_{A}}{MU_{B}}=-\frac{\frac{\Delta U}{\Delta A}}{\frac{\Delta U}{\Delta B}}=-\frac{\Delta B}{\Delta A}$

Inserting the calculus it equates to

$MRS=-\frac{\frac{\partial U(A,B)}{\partial A}}{\frac{\partial U(A,B)}{\partial B}}$

### 2.5 The Policy Example
 **Is a tax credit on hybrid car purchases the government’s best choice to reduce fuel consumption and carbon emissions?**

We determined in [chapter 1](http://open.oregonstate.education/intermediatemicroeconomics/module-1#section1-6) that the relevant consumer decision between more miles driven and other consumption probably conforms to the standard assumptions about consumer choice. Therefore, using the Cobb-Douglas utility function to represent a consumer who likes to drive a car as well as consume other goods and who sees them as a trade-off (money spent on gas is money not spent on other consumer goods) is a good choice. It also has the benefits of both conforming to the assumptions and being flexible:

$U(MD,C)=MD^{a}C^{\beta }$

where $MD$ = miles driven and $C$= other consumption.

In fact, the function itself can be taken to real-world data, where the parameters can be estimated for this market, the market for miles driven in the consumer’s car.

> [Рисунок] **Figure 2.3** Graph of indifference curves for the policy example (https://open.oregonstate.education/app/uploads/sites/203/2022/07/23Artboard-1.svg)

[Рисунок](https://open.oregonstate.education/app/uploads/sites/203/2022/07/23Artboard-1.svg)

### Exploring the Policy Question

1. Would other preference types be more appropriate in this example?
2. What would have to be true for perfect complements to be the appropriate preference type to use to analyze this policy?
3. What would have to be true for perfect substitutes? Given that we are considering a “typical” consumer who drives, is it appropriate to choose a “typical” utility function?
4. Are we just guessing, or do we have some basis in theory to support our choice of “well-behaved” preferences or a Cobb-Douglas utility function?

**[REVIEW: TOPICS AND RELATED LEARNING OUTCOMES]**

#### 2.1 Utility Functions

**Learning Objective 2.1**: Describe a utility function.

#### 2.2 Utility Functions and Typical Preferences

**Learning Objective 2.2**: Identify utility functions based on the typical preferences they represent.

#### 2.3 Relating Utility Functions and Indifference Curve Maps

**Learning Objective 2.3**: Explain how to derive an indifference curve from a utility function.

#### 2.4 Finding Marginal Utility and Marginal Rate of Substitution

**Learning Objective 2.4**: Derive marginal utility and MRS for typical utility functions.

#### 2.5 Policy Example
 Is a Tax Credit on Hybrid Car Purchases the Government’s Best Choice?

**Learning Objective 2.5**: The Hybrid Tax Credit and customer utility

**[LEARN: KEY TOPICS]**

#### Terms

Utility

The number that a utility function assigns to a specific bundle.

Univariate functions

The dependent variable is plotted on the vertical axis and the independent variable is plotted on the horizontal axis, i.e., the graph of $f(x)=mx+b$.

Bivariate functions

Functions containing two potentially independent variables. If one variable is influencing another variable, then you will have bivariate data that has an independent and dependent variable.

Useful for understanding how utility increases with the increased consumption of both $A$ and $B$, i.e., the graph of $U=A^\frac{1}{2}B^\frac{1}{2}$.

Ordinal

A function that deals in ranking as opposed to pure quantification; they only indicate which bundle is better, more preferred, etc., but not how much better it is than another bundle. After application of positive monotonic transformation to an ordinal function, meaning the ordering is not changed, the new function will represent the same preferences. If an ordinal function is reported in utils, regardless of the amounts used there is no relationship implied, i.e., bundle $A$ having 10 utils and bundle $B$ having 20 utils does not imply bundle $B$ is two times as preferred as bundle $A$, only that it is more preferred.

Cardinal

The utility of the product measured with the help of the product’s weight, length, temperature, etc.

Util

A unit used to transform the logical utility of a product to empirical. The ordinal utility might say that the consumer prefers the apple to the orange. Cardinal utility might say that the apple provides 80 utils while the orange only provides 40 utils.

Contour line

A way to represent a 3-dimensional topographical map in a two-dimensional space.

Diminishing marginal utility

The additional utility a customer receives from a product diminishes with each additional iteration of the product the customer receives.

Example

***Table 2.2** Diminishing marginal utility*

| **Pizza slices** | **Utility** | **Marginal utility** |
|---|---|---|
| 1 | 10 |  |
| 2 | 18 | 8 |
| 3 | 24 | 6 |
| 4 | 28 | 4 |

As a customer consumes more and more slices of pizza, the additional utility having one more slice of pizza provides–satiating excess hunger, producing dopamine from a delicious flavor, etc.–decreases with each additional slice.

#### Graph

3D utility function and contour line

> [Рисунок] Figure 2.1 A 3D graph showing a graph of $U$ equals $A^{\frac{1}{2}}$ times $B^ {\frac{1}{2}}$ to the half power (https://open.oregonstate.education/app/uploads/sites/203/2023/01/fig2.1b.png)

#### Equations

Cobb-Douglas utility function

A utility function describing goods which are neither complements nor substitutes.

$U(A,B) = A^\alpha B^\beta$

Perfect complement utility function

A utility function that describes goods that are perfect complements. See table 2.1 for more details.

$U(A,B) = MIN[A,B]$

Perfect substitute utility function

A utility function that describes goods that are perfect substitutes. See table 2.1 for more details.

$U(A,B) = A + B$

Marginal rate of substitution $(MRS)$

$MRS=-\frac{MU_{A}}{MU_{B}}$

[Defined as](http://open.oregonstate.education/intermediatemicroeconomics/module-1#section1-4) the amount of one good a consumer is willing to give up to get one more unit of another good.

##### From $MU$ to $MRS$

There is a direct connection between marginal utility and the marginal rate of substitution. This connection varies somewhat by utility function. From our basic utility function, $U=U(A,B)$, $MRS$ is represented as

$MRS=-\frac{MU_{A}}{MU_{B}}$

Substitution results in the following simplification:

$MRS=-\frac{MU_{A}}{MU_{B}}=-\frac{\frac{\Delta U}{\Delta A}}{\frac{\Delta U}{\Delta B}}=-\frac{\Delta B}{\Delta A}$

Utilizing calculus:

$MRS=-\frac{\frac{\partial U(A,B)}{\partial A}}{\frac{\partial U(A,B)}{\partial B}}$

Marginal utility $(MU)$

$MU_{a}=\frac{\Delta U}{\Delta A}$

The additional utility a consumer receives from consuming one additional unit of a good.

Utility function

Functions that rank bundles of consumption goods by assigning a number to each, where larger numbers indicate preferred bundles.

Table Summarizing Utility Functions

***Table 2.1** Types of preferences and the utility functions that represent them*

| **Preferences** | **Utility function** | **Type of utility function** |
|---|---|---|
| Love of variety or “well behaved” | $U(A,B)=AB$ | Cobb-Douglas |
| Love of variety or “well behaved” | $U(A,B)=A^\alpha B^\beta$ | Cobb-Douglas |
| Love of variety or “well behaved” | $U(A,B)=\alpha ln(A)+\beta ln(B)$ | Natural log Cobb-Douglas |
| Perfect complements | $U(A,B) = MIN[A,B]$ | Min function |
| Perfect substitutes | $U(A,B)=A+B$ | Additive |

### Media Attributions

- “Fill ‘Er Up”
   ©
   Derek Bruff
   is licensed under a
   CC BY-NC (Attribution NonCommercial)
   license
- fig2.1-768×768 © Patrick M. Emerson is licensed under a
   CC BY-NC-SA (Attribution NonCommercial ShareAlike)
   license
- Figure 2.4.1 Diminish Marginal Utility © Patrick M. Emerson is licensed under a
   CC BY-NC-SA (Attribution NonCommercial ShareAlike)
   license
- Figure 2.5.1 Graph of indifference curves for the policy example © Patrick M. Emerson is licensed under a
   CC BY-NC-SA (Attribution NonCommercial ShareAlike)
   license

definition

A mathematical function that ranks bundles of consumption goods by assigning a number to each, where larger numbers indicate preferred bundles.

×

Close definition

The satisfaction a consumer gets from a specific bundle.

×

Close definition

Ordinal information does not apply a direct value to the comparison. If someone is faster, in an ordinal comparison we wouldn't say she is forty times faster, only that she is faster.

×

Close definition

Cardinal information points in a specific direction instead of just in a general order. In a race, the first-place finisher ran the race finished in exactly one hour and your friend finished in one hour and six minutes. The cardinal information allows you to know your friend was exactly 10 percent slower than the fastest runner.

The order the race was completed, therefore, is ordinal, but the times the runners completed the race with is cardinal.

×

Close definition

A util is a generic unit of measurement used for bundle comparisons. Because bundle comparisons for utility are ordinal, we have no specific units in which to determine preference. Instead, we assign utils as a way to talk in comparison about preferences.

Ten utils for bundle A and twenty utils for bundle B does not mean bundle B is preferred twice as much, as we've no idea what 10 utils and 20 utils derives from—all we know is that 20 is bigger than 10, and so B is preferred.

×

Close definition

The ordering of an ordinal function isn't changed in the process of transforming the equation.

×

Close definition

See [Section 1.5.1: Perfect Complements](http://open.oregonstate.education/intermediatemicroeconomics/chapter/module-1#section1-5-1).

Goods that consumers want to consume only in fixed proportions, i.e., airpods to an iPhone.

Perfect complement indifference curves have [right angles.](http://open.oregonstate.education/intermediatemicroeconomics/chapter/module-1#figure151)

×

Close definition

See [Section 1.5.2: Perfect Substitutes](http://open.oregonstate.education/intermediatemicroeconomics/chapter/module-1).

A good that makes a consumer just as well off as a fixed amount of another good, i.e., Morton and Diamond Crystal are brands of table salt. For most consumers, a teaspoon of one salt is always just as good as a teaspoon of the other.

The graph for a perfect substitute is a [straight-forward linear equation (y=mx+b)](http://open.oregonstate.education/intermediatemicroeconomics/chapter/module-1#figure152).

×

Close definition

The Cobb-Douglas functional form was first proposed as a production function in a macroeconomic setting, but its mathematical properties are also useful as a utility function describing goods which are neither complements nor substitutes.

×

Close definition

A consumer that conforms to the "well-behaved" conditions of consumer preferences, and thus the indifference curve for this consumer's choice problem behaves as expected.

×

Close definition

See [Section 1.1](http://open.oregonstate.education/intermediatemicroeconomics/chapter/module-1#section1.1).

Sometimes presented as *more-is-better*.

If bundle $A$ represents more of at least one good and no less of any other good than bundle $B$, then $A$ is preferred to $B$.

×

Close definition

The idea that customers prefer choices in their consumption. Suppose we are talking about miles driven in a month in comparison to the cost in gas it takes to do such a thing: a customer will rarely want to spend all of their money on gas for miles driven, but also will not be likely to choose simply to not drive at all. Thus, a preference for variety.

×

Close definition

A function with one variable.

×

Close definition

A function with two variables.

×

Close definition

See [Chapter 1](http://open.oregonstate.education/intermediatemicroeconomics/chapter/module-1).

A graph of all the combinations of bundles that a consumer prefers equally. In other words, the consumer would be just as happy consuming any of them.

×

Close definition

Wavy, circular lines employed on a two-dimensional topographic map that depict elevation on the ground. The distance between each contour line is set to represent a certain level of elevation with zero being sea level.

×

Close definition

See [Section 2.4](http://open.oregonstate.education/intermediatemicroeconomics/chapter/module-2#section2-4).

The additional utility a customer receives from consuming one additional unit of a good.

$MU_{a}=\frac{\Delta U}{\Delta A}$

or the change in utility from a change in the amount of A consumed, where $\delta$ represents a change of value in the item.

×

Close definition
