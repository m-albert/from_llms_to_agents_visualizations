"""
Scripted outputs of the stage scenes (stages 2-5): the words each model
writes and the next-word distribution shown for each of them. Not real
model output: written for clarity, to match the overview schematic and to
show the progression between the stages. Stage 3 overclaims ("proved
direct harm"); stage 4 catches exactly that in its thoughts; stage 5 looks
it up and cites its sources.

One line per pass:

    picked=p | alternative=p ... | SPECIAL=p ...

with probabilities in percent. "_" stands for a space ("Search_web"), unless
parse is called with space=None (tool names like search_wiki_files).
Special words not listed get 0 (shown as "<0.1%").
"""


def parse(spec, space="_"):
    records = []
    for line in spec.strip().splitlines():
        fields = [field.split() for field in line.split("|")]
        fields += [[]] * (3 - len(fields))

        def pairs(items):
            return [(word.replace(space, " ") if space else word, float(p) / 100) for word, p in (item.rsplit("=", 1) for item in items)]

        (word, p), = pairs(fields[0])
        records.append(dict(word=word, p=p, others=pairs(fields[1]), special=dict(pairs(fields[2]))))
    return records


def words(records):
    return [record["word"] for record in records]


# Stage 2: the base model continues the question like a page of questions
STAGE2 = parse("""
…and=31 | Microplastics=22 What=14 The=9 A=6
in=48 | about=21 what=9 for=6 how=4
seafood?=27 | food?=24 water?=18 children?=8 fish?=6
What=41 | And=17 How=12 Are=9 Is=7
do=46 | about=19 is=14 are=9 does=5
recent=52 | experts=14 studies=11 scientists=8 we=5
papers=71 | studies=18 reports=4 articles=3 data=2
say=83 | show=8 suggest=4 tell=2 find=1
about=94 | on=3 regarding=1 of=1 concerning=0.5
PFAS=29 | microplastics=27 nanoplastics=12 pesticides=8 BPA=6
""")

# Stage 3: a fluent answer that overclaims; STOP ends it
STAGE3 = parse("""
Studies=38 | Research=24 Recent=15 Microplastics=11 Scientists=5 | STOP=0.1
suggest=46 | show=23 indicate=14 have=7 link=4 | STOP=0.1
microplastics=81 | that=11 these=3 plastic=2 exposure=1
may=52 | can=21 are=12 could=8 pose=3
be=74 | cause=10 affect=7 harm=4 enter=2
linked=63 | harmful=13 associated=11 related=5 toxic=3
to=97 | with=2 by=0.5 in=0.3 through=0.2
inflammation.=34 | cancer.=14 hormone=11 heart=9 disease.=8 | STOP=2
A=34 | However,=15 More=12 Some=9 | STOP=18
landmark=38 | recent=27 large=12 small=8 2023=6
study=88 | paper=6 report=3 trial=1 review=1
proved=41 | found=29 suggested=17 linked=6 showed=4
direct=44 | that=21 harm=14 clear=8 serious=4
harm=76 | damage=11 effects=6 links=3 toxicity=2
in=81 | to=12 from=3 for=2 among=1
humans.=69 | people.=14 children.=6 adults.=4 patients.=3 | STOP=0.2
STOP=91 | More=3 However,=2 Further=1 This=1 | STOP=91
""")
STAGE3_CLAIM = "A landmark study proved direct harm in humans."

# Stage 4: private thoughts first (they catch the overclaim), then a careful answer
STAGE4 = parse("""
THINK=96 | Studies=2 Research=1 Recent=0.5 Microplastics=0.3 | THINK=96 ANSWER=1.2 STOP=0.1
Harm=31 | The=22 User=14 Papers=9 Evidence=8 | ANSWER=0.4
in=72 | to=15 from=6 for=4 of=2
humans=88 | people=6 children=2 adults=1 cells=1
proven?=46 | shown?=24 known?=11 clear?=8 likely?=4
Not=52 | Unclear.=17 Some=11 Only=7 Yes,=4
yet=79 | really=8 clearly=6 conclusively=3 directly=2
→=47 | so=24 then=11 and=6 but=4 | ANSWER=3
don't=58 | be=19 avoid=12 stay=5 no=3
overclaim.=44 | exaggerate.=21 overstate.=17 claim=6 speculate.=4 | ANSWER=2
ANSWER=89 | Also=3 Check=2 Maybe=1 Keep=1 | ANSWER=89 STOP=0.3 THINK=0.1
Microplastics=47 | Recent=21 Studies=14 Research=9 Evidence=5
are=58 | have=21 were=9 can=6 accumulate=3
found=61 | present=17 detected=12 common=4 everywhere=2
in=84 | throughout=7 inside=4 across=2 within=1
human=66 | the=18 our=7 blood=4 many=2
tissue,=49 | blood,=28 bodies,=12 organs,=6 tissues,=3
but=71 | yet=12 and=9 though=4 while=2
harm=39 | health=24 effects=18 their=9 proof=4
is=82 | remains=11 has=3 isn't=2 to=1
still=57 | not=27 unclear.=9 unproven.=4 uncertain.=2
unclear.=63 | unproven.=17 debated.=8 uncertain.=6 unknown.=4 | STOP=0.5
STOP=93 | More=3 Further=1 However,=1 Studies=0.5 | STOP=93
""")

# Stage 5: thinks, calls a tool while thinking...
STAGE5_CALL = parse("""
THINK=97 | Studies=1 Research=0.5 Recent=0.3 Microplastics=0.2 | THINK=97 ANSWER=1 TOOL=0.8 STOP=0.1
Need=36 | Harm=22 The=14 User=9 Recent=6 | ANSWER=0.8 TOOL=1.5
sources=54 | papers=21 evidence=12 to=8 recent=4
first.=49 | for=19 to=12 here.=8 before=5 | TOOL=6 ANSWER=1
TOOL=88 | Let=4 Search=3 I=1 First=1 | TOOL=88 ANSWER=4 STOP=0.2
Search_web=92 | Read_files=4 Execute_code=1 search=1 Search=0.5
“microplastics=76 | “recent=9 “health=6 “papers=3 “plastic=2
health=68 | human=14 effects=9 papers=4 studies=2
publication”=41 | studies”=22 research”=18 review”=7 2024”=4
""")

# ...the software runs it and adds the result...
STAGE5_PAPERS = [
    dict(title="Microplastics in human blood and tissue", finding="found in nearly all samples"),
    dict(title="The effects of microplastics on health", finding="no proven harm in humans yet"),
]

# ...and the model answers from the result, citing it
STAGE5_ANSWER = parse("""
ANSWER=87 | Two=4 Paper=3 Both=2 Results=1 | ANSWER=87 TOOL=5 STOP=0.2
Microplastics=52 | Two=14 Recent=12 Studies=9 Papers=5
are=63 | have=18 were=10 accumulate=4 appear=2
found=72 | present=12 detected=10 common=2 everywhere=1
in=91 | throughout=4 inside=2 across=1 within=1
human=81 | the=9 our=4 blood=3 many=1
blood=64 | tissue=19 bodies=8 organs=4 cells=2
and=77 | samples=13 vessels=4 or=2 cells=1
tissue=82 | organs=9 placenta=3 lungs=2 brain=1
(Paper=92 | samples=3 worldwide=2 tissues=1 too=1
1).=96 | 2).=2 1)=1 1,=0.5 1.=0.3
Whether=38 | Their=21 But=17 However,=12 Health=6 | STOP=4
they=74 | this=12 microplastics=8 it=3 these=1
harm=69 | affect=14 cause=8 damage=4 threaten=2
health=81 | humans=8 people=5 us=2 organs=1
is=92 | remains=5 has=1 was=1 isn't=0.5
not=64 | still=24 unclear=6 yet=3 unknown=2
yet=83 | fully=8 clearly=5 conclusively=2 proven=1
proven=88 | known=6 clear=3 established=2 settled=1
(Paper=94 | in=2 by=1 and=1 for=0.5
2).=97 | 1).=2 2)=0.5 2,=0.2 2.=0.1
STOP=95 | More=2 Further=1 However,=1 This=0.5 | STOP=95
""")
