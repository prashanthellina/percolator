# Percolator

Performs the inverse of document search. A typical search operation involves a query and many documents. The process involves finding out which documents match the specified query. However the inverse process involves having a document and a many queries and finding out which queries would match the specified document.

## Installation

``` bash
sudo pip install git+git://github.com/prashanthellina/percolator.git
```

## Usage

### As a command-line tool

Some sample queries

``` bash
cat tests/queries
US
mcconnel OR obama
NBA
US AND Thai
```

Sample text (one title per line)

``` bash
cat tests/text
Blasts at market kill 118 in central Nigeria, official says
McConnell wins primary in Kentucky, CNN projects he'll face Grimes
Obama administration to release drone memo on killing US citizens
Just In: Celts drop to sixth pick in NBA draft
Fed Officials: Rate-Hike Tack Will Be Flexible
NBA commissioner: 'We're doing the right thing' to Donald Sterling
US urges Thai army to respect 'democratic principles'
Oscar Pistorius to start psychiatric evaluation next week, trial postponed to June 30
Pennsylvania Gay Marriage Ban Thrown Out as Divide Evens
Missouri execution halted by federal appeals court
Are there any GM cars that haven't been recalled?
Target Fires Chief of Unit in Canada, Which Lags
US STOCKS SNAPSHOT-Wall St ends lower in broad selloff; retail stocks weigh
JPMorgan Committing $100 Million Over 5 Years to Aid Revitalization in Detroit
Microsoft Introduces a Larger-Screen Surface Tablet
China bans government purchases of Windows 8, surprising Microsoft
Chuck E. Cheese's: Where a Kid Can Be a Kid With Oculus Rift
```

Run the command

``` bash
cd percolator/tests
percolator queries text
```

Output

``` bash
Building the percolator ...

Adding query "US" ...:  qid: 7516fd43adaa5e0b8a65a672c39845d2
Adding query "mcconnel OR obama" ...:  qid: d1c332b723b7f9228d635bed0e831087
Adding query "NBA" ...:  qid: 52b6d6fc82db6aef110362f4755a1fe8
Adding query "US AND Thai" ...:  qid: 049d777fe8c7a4ad1876be18083130ad

Percolating ...

0: Blasts at market kill 118 in central Nigeria, official says

1: McConnell wins primary in Kentucky, CNN projects he'll face Grimes

2: Obama administration to release drone memo on killing US citizens
        matched: d1c332b723b7f9228d635bed0e831087: "mcconnel OR obama"
        matched: 7516fd43adaa5e0b8a65a672c39845d2: "US"

3: Just In: Celts drop to sixth pick in NBA draft
        matched: 52b6d6fc82db6aef110362f4755a1fe8: "NBA"

4: Fed Officials: Rate-Hike Tack Will Be Flexible

5: NBA commissioner: 'We're doing the right thing' to Donald Sterling
        matched: 52b6d6fc82db6aef110362f4755a1fe8: "NBA"

6: US urges Thai army to respect 'democratic principles'
        matched: 049d777fe8c7a4ad1876be18083130ad: "US AND Thai"
        matched: 7516fd43adaa5e0b8a65a672c39845d2: "US"

7: Oscar Pistorius to start psychiatric evaluation next week, trial postponed to June 30

8: Pennsylvania Gay Marriage Ban Thrown Out as Divide Evens

9: Missouri execution halted by federal appeals court

10: Are there any GM cars that haven't been recalled?

11: Target Fires Chief of Unit in Canada, Which Lags

12: US STOCKS SNAPSHOT-Wall St ends lower in broad selloff; retail stocks weigh
        matched: 7516fd43adaa5e0b8a65a672c39845d2: "US"

13: JPMorgan Committing $100 Million Over 5 Years to Aid Revitalization in Detroit

14: Microsoft Introduces a Larger-Screen Surface Tablet

15: China bans government purchases of Windows 8, surprising Microsoft

16: Chuck E. Cheese's: Where a Kid Can Be a Kid With Oculus Rift
```

### As a library

``` python
>>> import percolator
>>> p = percolator.Percolator()

>>> p.add_query(u'apple OR orange')
'07d82a36fafc4885e63fa8881280131c'
>>> p.add_query(u'apple AND orange')
'378681af3fb0fbc73901aaa217079c7c'

>>> p.get_matches(u'I ate an Apple')
set(['07d82a36fafc4885e63fa8881280131c'])

>>> p.get_matches(u'I ate an Apple but not an orange')
set(['07d82a36fafc4885e63fa8881280131c', '378681af3fb0fbc73901aaa217079c7c'])
```
