"""
Scripted outputs of the two example bots (WikiSearchBot, CourseTutorBot),
in the format of scenes/stage_outputs.py. Not real model output: written
to make each implementation's steps easy to follow. Tool names contain
"_", so these are parsed with space=None (no word contains a space).
"""
from scenes.stage_outputs import parse


# Wiki search bot: thinks, searches the downloaded wiki pages...
WIKI_CALL = parse("""
THINK=97 | Raw=1 Save=0.5 The=0.3 You=0.2 | THINK=97 ANSWER=1 TOOL=1.5 STOP=0.1
Check=41 | Search=24 Look=12 Need=9 Find=6 | ANSWER=0.5 TOOL=3
the=72 | wiki=14 pages=6 first.=4 sources=2
wiki.=63 | wiki=18 pages.=9 docs.=5 rules.=2 | TOOL=4 ANSWER=1
TOOL=91 | Raw=3 Search=2 The=1 Images=1 | TOOL=91 ANSWER=3 STOP=0.1
search_wiki_files=96 | search=2 Search=1 read=0.5 find=0.3
<raw=58 | <microscope=17 <images=11 <storage=7 <save=4
images>=71 | data>=12 image>=8 storage>=5 files>=2
""", space=None)

# ...which returns the file name and the text around each match...
WIKI_FILES = [
    dict(file="storage.md", page="Data storage"),
    dict(file="microscopes.md", page="Microscopes"),
    dict(file="booking.md", page="Booking"),
    dict(file="software.md", page="Software"),
]
WIKI_MATCHES = [
    dict(file="storage.md", snippet="…save raw images on the group share, folder raw/. Never delete them…"),
    dict(file="microscopes.md", snippet="…export raw images as .czi, not .png…"),
]
WIKI_SEARCH = "raw images"

# ...and answers from the matches, citing the pages
WIKI_ANSWER = parse("""
ANSWER=88 | Raw=3 Both=2 Two=2 Save=1 | ANSWER=88 TOOL=4 STOP=0.2
Save=46 | Store=22 Put=14 Raw=9 Use=4
them=61 | raw=19 your=11 the=6 all=2
on=83 | in=11 to=4 at=1 onto=0.5
the=88 | your=7 our=3 a=1 group=0.5
group=91 | lab=4 shared=3 network=1 team=0.5
share,=58 | share=29 drive=7 server=4 folder=1
folder=74 | in=17 under=6 at=2 path=1
raw/,=62 | raw/=21 raw,=9 /raw=5 data/=2
and=69 | never=14 but=9 do=4 then=2
never=87 | don't=8 do=3 always=1 keep=0.5
delete=91 | remove=5 move=2 edit=1 change=0.5
them=82 | raw=11 the=4 these=2 any=0.5
(storage.md).=93 | (microscopes.md).=4 here.=1 afterwards.=1 later.=0.5
Export=41 | Save=22 Use=16 Keep=9 Also,=6 | STOP=6
them=79 | as=14 raw=4 images=2 files=0.5
as=91 | in=5 to=2 with=1 into=0.5
.czi,=72 | .czi=17 .tif,=6 .png,=3 .czi.=1
not=88 | never=7 since=3 because=1 so=0.5
.png=81 | .png,=12 .jpg=4 .tif=2 PNG=0.5
(microscopes.md).=94 | (storage.md).=3 files.=1 images.=1 ever.=0.5
STOP=95 | More=2 See=1 Also,=1 Ask=0.5 | STOP=95
""", space=None)


# Course tutor: thinks, reads the student's notebook cell...
TUTOR_CALL_CODE = parse("""
THINK=96 | Your=1 My=1 Segmentation=0.5 Check=0.4 | THINK=96 ANSWER=1.5 TOOL=1 STOP=0.1
Look=37 | Check=29 Read=13 First,=9 Their=5 | TOOL=4 ANSWER=0.5
at=83 | into=7 over=4 for=2 closely=1
their=58 | the=27 cell=7 code=4 student's=2
code.=66 | code=17 cell.=9 notebook.=5 mask.=2 | TOOL=4 ANSWER=1
TOOL=91 | What=3 Cell=2 The=1 Maybe=1 | TOOL=91 ANSWER=3 STOP=0.1
read_code=93 | read_solution=5 read=1 code=0.5 run=0.3
<4>=88 | <cell=6 <3>=3 <5>=2 <all>=1
""", space=None)

# ...then the exercise solution, which the student can't see...
TUTOR_CALL_SOLUTION = parse("""
Threshold=33 | The=24 img=14 Mask=11 Everything=7 | ANSWER=3 TOOL=2
0=61 | too=13 is=11 at=6 value=4
is=79 | keeps=9 marks=6 means=4 makes=2
too=68 | way=11 far=8 the=5 very=3
low.=72 | small.=14 low:=6 low,=4 simple.=2 | ANSWER=6 TOOL=2
Compare=31 | Check=29 What=12 Look=9 See=6 | ANSWER=9 TOOL=4
with=74 | to=16 against=6 the=2 solution.=1
the=81 | solution.=11 exercise=4 their=2 my=1
solution.=77 | exercise.=12 reference.=6 answer.=3 notes.=1 | TOOL=8 ANSWER=1
TOOL=89 | Expected=4 The=3 Exercise=2 Otsu=1 | TOOL=89 ANSWER=5
read_solution=94 | read_code=4 read=1 solution=0.5 run=0.2
<3>=91 | <4>=5 <exercise=2 <2>=1 <1>=0.5
""", space=None)

TUTOR_NOTEBOOK = "exercise_3.ipynb"
TUTOR_CELL = 4
TUTOR_CODE = [
    'img = io.imread("nuclei.tif")',
    "mask = img > 0",
    "labels = measure.label(mask)",
    "labels.max()",
]
TUTOR_OUTPUT = "1"
TUTOR_SOLUTION_FILE = "exercise_3.py"
TUTOR_SOLUTION = [
    "t = filters.threshold_otsu(img)",
    "mask = img > t",
]
TUTOR_FILES = ["exercise_1.py", "exercise_2.py", "exercise_3.py", "exercise_4.py"]

# ...and gives a hint towards the next step, not the solution
TUTOR_ANSWER = parse("""
It=34 | Solution=27 Otsu=13 Uses=9 They=6 | ANSWER=4
uses=72 | needs=11 picks=8 computes=5 sets=2
Otsu.=58 | Otsu's=17 a=8 an=3 automatic=2 | ANSWER=7
Hint,=43 | Give=22 Don't=14 Only=9 Hint=6 | ANSWER=6
not=51 | don't=26 no=14 never=4 only=2
the=74 | code.=13 solution.=8 answer.=3 a=1
code.=69 | solution.=19 answer.=7 fix.=3 line.=1 | ANSWER=9
ANSWER=88 | Also=3 Ask=3 Mention=2 Maybe=1 | ANSWER=88 TOOL=2 STOP=0.3
Look=38 | Check=31 Your=12 The=9 Try=4
at=86 | closely=5 again=4 into=2 back=1
your=79 | the=16 line=3 cell=1 mask=0.5
threshold:=57 | threshold.=19 mask:=11 threshold=8 line=3
with=46 | img=21 almost=14 at=9 using=5
img=73 | a=11 0,=7 zero,=5 this=2
>=88 | <=6 ≥=3 *=1 +=1
0,=81 | 0=9 zero,=5 1,=3 10,=1
almost=48 | nearly=21 every=14 all=9 most=5
every=83 | all=11 each=4 any=1 the=0.5
pixel=86 | value=6 pixels=4 point=2 spot=1
counts=41 | is=33 becomes=11 ends=7 looks=4
as=93 | for=3 in=2 like=1 toward=0.5
foreground.=58 | foreground,=16 nucleus.=12 signal.=8 object.=3 | STOP=3
Which=34 | Try=26 Plot=13 What=11 Look=7 | STOP=4
value=71 | threshold=16 level=7 number=3 intensity=2
separates=67 | splits=14 divides=9 between=4 marks=3
nuclei=79 | cells=11 objects=5 the=3 signal=1
from=91 | and=6 vs=2 versus=1 to=0.5
background?=88 | background=6 noise?=3 the=2 dark?=1 | STOP=1
STOP=94 | Hint:=2 Tip:=1 Try=1 Also,=1 | STOP=94
""", space=None)
