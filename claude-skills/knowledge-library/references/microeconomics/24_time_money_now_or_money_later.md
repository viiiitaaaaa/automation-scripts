# 24. Time: Money Now or Money Later?

> Источник: Patrick M. Emerson, *Intermediate Microeconomics*, Oregon State University, 2019. https://open.oregonstate.education/intermediatemicroeconomics/chapter/module-24/
> Лицензия: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/) — только некоммерческое использование, с указанием автора, производные — под той же лицензией. Текст сконвертирован в markdown без изменений по смыслу; формулы — LaTeX в `$...$`; рисунки — ссылками.

### The Policy Question
 **Should the government regulate the Payday Loan industry?**

The term **payday lenders** describes businesses that provide short-term credit to generally more risky borrowers. They often charge high interest rates, and that has led them to become the target of government regulators who are concerned that they are unfairly taking advantage of a vulnerable population that is forced to accept terms that are unfavorable and damaging. Defenders of the businesses suggest that they are simply filling a need and that high interest rates are determined by the market and are a consequence of low repayment rates.

### Exploring the Policy Question

1. What is payday lending?
2. What is the justification for government regulations that place restrictions on the industry?

**[Learning Objectives]**

#### 24.1 Present Discounted Value

**Learning Objective 24.1**: Explain how money in the future and in the past is given a value in the present.

#### 24.2 Inflation

**Learning Objective 24.2**: Describe how inflation is accounted for in present value calculations.

#### 24.3 Choices over Time

**Learning Objective 24.3**: Describe how individuals can use present value to make decisions over time.

#### 24.4 Interest Rates

**Learning Objective 24.4**: Explain how interest rates are determined and how they change.

#### 24.5 Policy Example
 **Should the Government Regulate the Payday Loan Industry?**

**Learning Objective 24.5**: Apply knowledge of time in economics to evaluate the role of payday lenders and to determine if there is a role for the regulation of such lenders.

### 24.1 Present Discounted Value

**Learning Objective 24.1**: Explain how money in the future and in the past is given a value in the present.

Your grandmother gives you a savings bond that will pay you exactly $100 in one year. You cannot cash it in until its maturity date, so it is not convertible into money until exactly one year. This chapter is about how we value money and other costs and benefits across time. The main force that determines the value of money across time is interest rates. Interest rates determine the return an individual gets for allowing others to use their money for a period of time. Formally, an **interest rate** is a percentage extra of an amount of money that must be paid to borrow that money for a fixed period of time. For example, if you put $1,000 into a savings account that pays a simple 3 percent annual interest rate, $i$, then after one year, you would have

$$1,000(1+i) = $1,000(1+.03) = $1,000^*(1.03) = $1,030$

The interest rate allows us to do such calculations: determine the amount of money a person will gain after a determined amount of time from an investment or savings.

The **discount rate** is the method of placing a value on future consumption relative to present consumption. In general, individuals do not like to wait to consume, and waiting is a cost. The discount rate is a measure of the cost of waiting for consumption. Discount rates are personal; each individual has their own depending on how much they dislike waiting for consumption in the future. A person’s willingness to lend money depends crucially on the discount rate. If a person has a very low discount rate, meaning that consumption in the future is almost as desirable as consumption today, they would be willing to loan money for a low interest rate. On the other hand, if they had a high discount rate, it would take a high interest rate to get them to lend money because lending that money means it is not available to fund current consumption.

**Compounding** is the process by which a sum of money, the principle, placed in an account that earns interest periodically, will grow based on the interest earned by the principle and by the subsequent interest payments.

For example, if $1,000 is in a savings account that pays 3 percent interest annually, it will earn $30 after a year. If that interest is withdrawn, leaving $1,000 for the second year, it would earn another $30, for a total interest income of $60. So after five years, the total interest earned would be $150, leaving a total of $1,150. If instead the interest income is left in the account after the first year, in the second year, the account would earn interest on the $1,030, or it would earn

$$1,030(1.03) = $1,060.90$

Thus, the process of compounding interest leads to an additional $0.90 in interest. After five years, the total is

$$1,000(1.03)(1.03)(1.03)(1.03)(1.03)$ or $$1,000(1.03)^5 = $1,159.27$

The additional interest earned with compounding is $9.27 over five years.

The general formula for the growth of money where the interest is left to accumulate is

$P(1+i/n)^{nt}$

where $P$ is the original amount of money; the principle, $i$, is the interest rate in decimal terms; $n$ is the number of times per year the interest is paid; and $t$ is the number of years the principle and interest sit in the account. The more frequently the interest is paid, the faster the money in the account will grow. In the example above, suppose interest is paid quarterly rather than annually; instead of being paid once a year, it is paid four times a year. Applying the formula, we get

$$1,000(1+ 03/4)^{20} = $1,161.18$

The more frequent interest payment leads to $11.18 in interest income versus the $9.27 earned with annual payments.

When growth is continuous, the exponential function describes the rate of growth. This is used to calculate things like population growth but also for accounts that pay and charge interest continuously, like many bank accounts, savings vehicles, and loans. The formula for the growth of money where the interest is left to accumulate for accounts that pay interest continuously is $Pe^{it}, where [latex]e$ is the exponential function (expressed as “exp” on some calculators). This leads to the most rapid growth in money in an account. Using our example from before, the calculation is

$$1,000e^{(0.3)5}= $1,161.83$

Now that we know how interest rates work and are calculated, we can use them to calculate both future values, like we have been doing above, and present values. **Future value ($FV$)** is the value a sum of money is worth after a period of time if placed into an interest-earning account and left to accrue compound interest. **Present value ($PV$)** is what an amount of money that will be paid in the future is worth today given the interest rate. The best way to understand present value is to ask the question, How much money would I need to put into an account that earns the market interest rate today to have X amount of money at a specific time in the future? For example, if the market interest rate is 3 percent and the basic savings account pays interest annually, then the amount of money you would need to place into a savings account today in order to have $103 in exactly one year is $100. So the present value of $103 in a year is $100. Expressed as a formula, we would say that

$PV(1.03) = $103$

Solving for $PV$ yields

$PV = ($103/1.03) = $100$

In general the formula for $PV$ is

$PV = FV/(1+i)^t$

for annual interest payments. For more frequent payments, the formula is

$PV = FV/(1+i/n)^{nt}$

For continuous interest payments, the formula becomes

$PV = FV/e^{it}$.

As a final example, suppose you have a bond that will pay $5,000 in exactly six years. If the market interest rate is 4.2 percent and accounts are paid continuously, the present value of the sum is

$PV = $5,000/e^{(.042)6} = $3,886.22$

Remember that $3,886.22 is the exact amount of money you could put into an account that pays 4.2 percent interest continuously, and if you left the accrued interest in the account, in exactly six years, you would have $5,000. In this way, we can compare the value of money through time, both in the future and in the present.

### 24.2 Inflation

**Learning Objective 24.2**: Describe how inflation is accounted for in present value calculations.

In the future and present value calculations we made above, we ignored inflation. But in general, prices tend to rise over time. So though we calculate the amount of money we could put in a bank account today to have a precise sum after a fixed period of time, that sum might not buy as much if prices have risen over that time. In other words, the amount of *consumption* that $100 allows falls over time if *nominal* prices rise. What we have done in the previous section is calculate present value in nominal terms, but what we generally want is to calculate present value in real terms using real, not nominal, prices. For example, if someone asks you to lend them $10 to buy a cheeseburger, you might want to make sure that when they repay it in a year, they repay you enough money to buy the same cheeseburger. If the price of the burger has risen to $12, then you would need to be repaid $2 more to compensate for the price inflation. In real terms, the $12 in a year is the same as $10 today.

To adjust for inflation, $g$, we have to take it into account for our present value calculations. Let’s start with an example of a $100 debt that is due to be repaid in exactly one year. Suppose that inflation is 2 percent, or $g = .02$. The real amount you need to repay is $100, but the nominal amount is $$100(1+g)$, or $102. This is how much you would need to repay for the lender to be able to buy the same amount of consumption as they could with $100 a year ago. Alternatively, the real value today of $102 paid in a year is $100.

To calculate the real present value of this future payment, we have to use the interest rate as before. To keep it in real terms, we need to convert the nominal interest rate to a real interest rate by adjusting it for inflation using the inflation rate. If $r$ is the real interest rate, say 3 percent, then the value of $100 next year is $103 in real terms. To convert this to the nominal value, we have to multiply by $(1+g)$, as seen above. If $g$ is 2 percent, then we multiply $103 by (1+.02) to get $105.06. This is the amount that the borrower would have to repay in order for the real value of the repayment to be a 3 percent gain.

Note that the formula for this calculation is

$P(1+r)(1+g)$

where $P$ is the principle amount (in this case $100). From this, it is possible to describe the general formula for the nominal interest rate, $i$, as

$1+i = (1+r)(1+g)$

Solving for $i$ yields

$i = r + r g + g$

Solving this equation for $r$ yields

$r=\frac{i-g}{1+g}$

Note that if the interest rates and inflation rates are low, then $1+g$ is very close to 1, and the relationship between the real and nominal interest rates can be approximated as

$r \approx i-g$

or the nominal interest rate minus inflation. In our example, the approximation is that the real interest rate is the nominal interest rate, 3 percent, minus the inflation rate, 2 percent, which is 1 percent. Since $(.03–.02)/(1+.02)$ equals .098, or .98 percent, you can see the approximation is very close but not exactly the real interest rate.

To calculate the real present value of a sum of money, we use the real interest rate rather than the nominal interest rate. For example, using our values for nominal interest rates and inflation, we can calculate the value of $100 in a year as worth $$100/(1+.0098)$, or $99.03 in real terms. Note that in nominal terms, this would be $$100/(1+.03)$, or $97.09. The difference is the erosion in the real value of the money due to inflation over the year. If you put $97.09 in an account earning 3 percent interest, you would get exactly $100 in a year, but that $100 in a year would not buy the same amount of consumption as $100 today would. So in order to get the same consumption as $100 today in a year, you need to put $99.03 in the account today (and you would get $102 in nominal dollars in a year, which is exactly $100 times the inflation rate).

### 24.3 Choices over Time

**Learning Objective 24.3**: Describe how individuals can use present value to make decisions over time.

Now that we now know how to evaluate money and consumption across time, we can begin to study decisions across time. Let’s start with an example: The owner of a business can invest in a new production technology that will increase profits by $150,000 a year for five years. The cost of this technology is $450,000. Should the owner make this investment?

Without thinking about time, you might think the answer is immediately obviously yes, as the stream of extra profits is $750,000 and the cost is $700,000. However, by using this logic, we are ignoring the fact that the owner has to wait for the extra profits. In order to compare the $700,000 expenditure today to the future profits, we need to bring the future profits into the present. To do so, we need the interest rate, so for this example, suppose the real interest rate is 2 percent. Our calculation, then, is

$PV=\left[\frac{\$150,000}{(1+r)^1}+\frac{\$150,000}{(1+r)^2}+\frac{\$150,000}{(1+r)^3}+\frac{\$150,000}{(1+r)^4}+\frac{\$150,000}{(1+r)^5}\right]$.

Note that each of the payments is appropriately brought into real present value terms based on the formula and summed together. Since the real present value of the return on the investment is $694,655.13 and the real present cost of the investment is $700,000, the answer to our question is actually no, the owner should not make the investment.

A different way to think about the same kind of investment decisions is to think about the **net present value**, which considers the difference between the present value of the benefits of an action and the present value of the costs of the action. A rational economic actor such as a firm should undertake an investment only if the present value of the returns on the investment, $R$, is greater than the present value of the costs of the investment, $C$, or if $R > C$. Since net present value ($NPV$) is simply the difference between the two, the statement is equivalent to saying that the investment should only happen if net present value is positive, which gives us this rule:

$NPV=R-C \gt 0$

To calculate this, assume that the initial year is $t = 0$, the firm’s revenue in year $t$ is $R_t$, and the firms cost in year $t$ is $C_t$. The stream of revenues and costs ends in year $T$. The net present value rule is the following:

$NPV = R—C$
 $= \left [ R_0+ \frac{R_1}{(1+r)^1}+ \frac{R_2}{(1+r)^2}+...+\frac{R_T}{(1+r)^T} \right ]- \left [ C_0+\frac{C_1}{(1+r)^1}+\frac{C_2}{(1+r)^2}+...+\frac{C_r}{(1+r)^T} \right ]\gt0$

Note that revenue minus costs is similar to profit and is profit if fixed and opportunity costs are included in

$C:\Pi_t = R_t—C_t$

We can rewrite the $NPV$ rule as a cash-flow rule (or profit rule) that states that a firm should only undertake an investment if the net present value of the cash flow is positive. We can do this by rearranging terms in the expression above:

$NPV=\left[R_0-C_0+\frac{R_1-C_1}{(1+r)^1}+\frac{R_2-_2}{(1+r)^2}+...+\frac{R_T-C_T}{(1+r)^T}\right]$
 $=\left[\Pi_0+\frac{\Pi_1}{(1+r)^1}+\frac{\Pi_2}{(1+r)^2}+...+\frac{\Pi_T}{(1+r)^T}\right]\gt0$

The expression makes clear that the decision to make an investment that has revenues and costs into the future depends not on the annual cash flow but on the present value of the net cash flow so that even an investment that has years in which there is a negative return in cash-flow terms can be a good investment over the life of the investment. For example, consider an investment that costs $50 million in the first year and $20 million a year for two more years. In the first year, there is no revenue; in the second, revenue is $10 million; and in the third, revenue is $100 million. Using the NPV formula with a real interest rate of r = 3 percent, we get the following:

$NPV=-$50+\frac{$10-$20}{1.03}+\frac{$100-$20}{(1.03)^2}$$=-$50+\frac{-$10}{1.03}+\frac{$80}{1.0609}$$=-$50-$9.7+$75.4$
 $=$15.7\gt0$

So the firm should make this investment even though cash flow is negative for the first two years.

### 24.4 Interest Rates

**Learning Objective 24.4**: Explain how interest rates are determined and how they change.

Interest rates determine investment decisions. At the most basic level, interest rates represent the opportunity cost of investing money if the alternative is to put the money into an interest-earning savings account. But where does the market interest rate get determined? The market for borrowing and lending money is called the **capital market**, where the supply is the number of funds loaned, the demand is the number of funds borrowed, and the price is the interest rate itself. The capital market is a competitive market, and as such, the interest rate is determined in equilibrium. The market interest rate is the rate at which the number of funds supplied equals the number of funds demanded.

> [Рисунок] **Figure 24.4.1** Capital market equilibrium (https://open.oregonstate.education/app/uploads/sites/203/2022/08/24.4.1-e1672788089502.png)

In **figure 24.1**, the capital market is initially in equilibrium at $i_1$, $Q_1$. The supply curve represents the number of funds offered to loans and is upward sloping because as interest rates rise, more funds are made available because of the higher return on loans. The demand curve represents the number of funds desired to borrow and is downward sloping because as interest rates fall, more funds are desired due to the lower expense of borrowing. At interest rate $i_1$, the number of funds demanded equals the number of funds supplied, $Q_1$.

The demand curve will shift based on opportunities to invest, a person needing funds to pay expenses like buying a house or paying for college, governments needing money to build roads and buildings, firms needing money to make new investments in plants and equipment, and so on. The supply curve will shift based on things like changes in tax policy that incentivize retirement investment, increased investment among foreigners, or the government’s policy to buy back government bonds to increase the money supply. In **figure 24.1**, the supply curve shifts to the right, perhaps due to a new tax policy that incentivizes savings. The effect of the increased supply of funds leads to a lower interest rate, $i_2$, and a greater amount of funds lent and borrowed, $Q_2$.

### 24.5 Policy Example
 **SHOULD THE GOVERNMENT REGULATE THE Payday LOAN INDUSTRY?**

**Learning Objective 24.5**: Apply knowledge of time in economics to evaluate the role of payday lenders and to determine if there is a role for the regulation of such lenders.

**Payday loans** refer to loans that have a number of common features. The loans are generally small; $500 is a common loan limit. The loans are usually repaid in a single payment on the borrower’s next payday (hence the name). Loans are typically from two to four weeks in duration. Most lenders do not evaluate individual borrowers’ ability to repay the loan. As the [US Consumer Financial Protection Bureau](https://www.consumerfinance.gov/ask-cfpb/what-is-a-payday-loan-en-1567/) states,

> Many state laws set a maximum amount for payday loan fees ranging from $10 to $30 for every $100 borrowed. A typical two-week payday loan with a $15 per $100 fee equates to an annual percentage rate (APR) of almost 400 percent. By comparison, APRs on credit cards can range from about 12 percent to about 30 percent. In many states that permit payday lending, the cost of the loan, fees, and the maximum loan amount are capped.

Critics of payday lenders argue that the effective interest rates they charge (in the form of fees) are exorbitantly high and that these lenders are taking advantage of people with no other source of credit. The lenders themselves argue that credit markets are competitive and therefore the interest rates they charge are based on the market for small loans to people with very high default rates. The fact that borrowers are willing to pay such high rates suggests that the need for short-term credit is very high. On the other hand, critics suggest that the willingness to pay such high rates is evidence that consumers do not fully understand the costs or are driven out of desperation to borrow.

As seen in the quote above, many states have responded to the growth in payday lending with regulations that cap the loan amounts and limit the fees that the lenders can charge. Governments worry about low-income people being trapped in a cycle of debt, which effectively lowers their incomes even further due to the payment of fees. This does not address the source of the problem, however, which is the cause of the need for short-term credit itself.

**[Review: Topics and Related Learning Outcomes]**

#### 24.1 Present Discounted Value

**Learning Objective 24.1**: Explain how money in the future and in the past is given a value in the present.

#### 24.2 Inflation

**Learning Objective 24.2**: Describe how inflation is accounted for in present value calculations.

#### 24.3 Choices over Time

**Learning Objective 24.3**: Describe how individuals can use present value to make decisions over time.

#### 24.4 Interest Rates

**Learning Objective 24.4**: Explain how interest rates are determined and how they change.

#### 24.5 Policy Example
 **Should the Government Regulate the Payday Loan Industry?**

**Learning Objective 24.5**: Apply knowledge of time in economics to evaluate the role of payday lenders and to determine if there is a role for the regulation of such lenders.

**[LEARN: KEY TOPICS]**

#### Terms

Interest rate

An interest rate is a percentage extra of an amount of money that must be paid to borrow that money for a fixed period of time.

Discount rate

The discount rate is the method of placing a value on future consumption relative to present consumption.

Compounding

Compounding is the process by which a sum of money, the principle, placed in an account that earns interest periodically, will grow based on the interest earned by the principle and by the subsequent interest payments.

Future value

Future value is the value a sum of money is worth after a period of time if placed into an interest-earning account and left to accrue compound interest.

Present value

Present value is what an amount of money that will be paid in the future is worth today given the interest rate.

Net present value

The net present value considers the difference between the present value of the benefits of an action and the present value of the costs of the action.

Capital market

The market for borrowing and lending money is called the capital market, where the supply is the number of funds loaned, the demand is the number of funds borrowed, and the price is the interest rate itself. The capital market is a competitive market, and as such, the interest rate is determined in equilibrium.

#### Graph

Capital market equilibrium

> [Рисунок] Figure 24.1 Capital market equilibrium (https://open.oregonstate.education/app/uploads/sites/203/2023/01/24.4.1c.png)

### Media Attributions

- Figure 24.4.1 Capital market equilibrium © Patrick M. Emerson is licensed under a
   CC BY-NC-SA (Attribution NonCommercial ShareAlike)
   license
