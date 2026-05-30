#!/usr/bin/env python3
"""
Main PDF Builder — combines all parts into one final PDF
"""

import sys
sys.path.insert(0, '.')

from reportlab.lib.units import inch
from reportlab.platypus import KeepTogether, Preformatted
from pdf_framework import (
    _table_box, _ps, build_doc, on_page,
    ST, CW, MARGIN, PW, PH,
    C_DARK_BLUE, C_MED_BLUE, C_ACCENT, C_LIGHT_BLUE, C_PY_BLUE, C_PY_YELLOW,
    C_CODE_BG, C_CODE_BDR, C_BEG_DARK, C_BEG_LIGHT, C_INT_DARK, C_INT_LIGHT,
    C_ADV_DARK, C_ADV_LIGHT, C_DIVIDER, C_DARK_GRAY, C_MED_GRAY, C_LIGHT_GRAY,
    C_TIP_BG, C_TIP_BDR, C_WARN_BG, C_WARN_BDR, C_ALT_ROW, C_OUT_BG, C_OUT_BDR,
    C_OUT_HDR, C_TEAL, C_TEAL_LIGHT, C_PURPLE, C_PURPLE_L,
    h_bar, spacer, bullet_list, num_list, section_hdr, code_block, output_block,
    tip_box, warn_box, prob_header_row, complexity_table, concepts_chips,
    test_cases_table, section_banner, sub_banner, divider, light_divider,
    HexColor, white, black,
    Paragraph, Spacer, PageBreak, Table, TableStyle, HRFlowable,
    TA_LEFT, TA_CENTER, TA_JUSTIFY, TA_RIGHT,
)
from problems_part1 import PROBLEMS
from problems_part2 import PROBLEMS_PART2

ALL_PROBLEMS = PROBLEMS + PROBLEMS_PART2

# ═══════════════════════════════════════════════════════════════════════════════
# COVER PAGE
# ═══════════════════════════════════════════════════════════════════════════════
def build_cover():
    story = []
    # Full-page dark background via tall table
    title_block = _table_box([
        [Paragraph('<b>PYTHON OOP</b>', _ps('ct1', fontName='Helvetica-Bold', fontSize=42,
            textColor=white, alignment=TA_CENTER, leading=50))],
        [Paragraph('Programming Challenges', _ps('ct2', fontName='Helvetica', fontSize=22,
            textColor=HexColor('#c5cae9'), alignment=TA_CENTER, leading=28))],
        [Paragraph('for Coding Interviews', _ps('ct3', fontName='Helvetica-Bold', fontSize=24,
            textColor=C_PY_YELLOW, alignment=TA_CENTER, leading=30))],
        [Spacer(1,18)],
        [Paragraph('25 Real-World Challenges  •  3 Difficulty Levels  •  Every Section Covered',
            _ps('ct4', fontName='Helvetica', fontSize=11, textColor=HexColor('#e8eaf6'),
            alignment=TA_CENTER, leading=16))],
        [Spacer(1,10)],
    ], [CW+0.06*inch], [
        ('BACKGROUND',(0,0),(-1,-1),C_DARK_BLUE),
        ('TOPPADDING',(0,0),(-1,-1),14),('BOTTOMPADDING',(0,0),(-1,-1),14),
        ('LEFTPADDING',(0,0),(-1,-1),30),('RIGHTPADDING',(0,0),(-1,-1),30),
    ])
    story.append(Spacer(1,0.5*inch))
    story.append(title_block)
    story.append(Spacer(1,0.3*inch))

    # Feature cards row
    feats = [
        ('🏗️','OOP Concepts','Classes • Inheritance\nPolymorphism • ABC'),
        ('🌍','Real Systems','25 Industry Problems\nBank to Smart Home'),
        ('📋','20 Sections','Full Solution • Tips\nDry Run • Test Cases'),
        ('📈','Complexity','Time & Space\nAnalysis per Problem'),
    ]
    feat_cells = []
    for icon,title,desc in feats:
        feat_cells.append(_table_box([
            [Paragraph(icon,_ps('fi',fontName='Helvetica',fontSize=22,alignment=TA_CENTER))],
            [Paragraph(f'<b>{title}</b>',_ps('ft',fontName='Helvetica-Bold',fontSize=10,
                textColor=C_DARK_BLUE,alignment=TA_CENTER))],
            [Paragraph(desc.replace('\n',' '),_ps('fd',fontName='Helvetica',fontSize=8.5,
                textColor=C_MED_GRAY,alignment=TA_CENTER))],
        ],[CW/4-0.1*inch],[
            ('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8),
            ('BACKGROUND',(0,0),(-1,-1),C_LIGHT_BLUE),
        ]))
    feat_row = _table_box([feat_cells],[CW/4]*4,[
        ('BOX',(0,0),(-1,-1),1,C_CODE_BDR),
        ('LINEBEFORE',(1,0),(3,0),1,C_CODE_BDR),
        ('TOPPADDING',(0,0),(-1,-1),0),('BOTTOMPADDING',(0,0),(-1,-1),0),
        ('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),0),
    ])
    story.append(feat_row)
    story.append(Spacer(1,0.25*inch))

    # Systems covered grid
    story.append(Paragraph('<b>Real-World Systems Included:</b>', ST['h3']))
    systems = ['Bank Account','ATM Machine','Hospital Billing','Hotel Booking',
               'Food Delivery','Library Mgmt','Employee Payroll','Student Grades',
               'Parking Mgmt','E-commerce Cart','Cab Booking','Airline Reservation',
               'Inventory Mgmt','Movie Tickets','Electricity Bill','Insurance Claims',
               'Vehicle Rental','Gym Membership','Online Exam','Warehouse Track',
               'Smart Home','School Mgmt','Hospital Queue','Subscription Bill','Loan Eligibility']
    cols = 5
    padded = systems + ['']*((-len(systems))%cols)
    rows = [padded[i:i+cols] for i in range(0,len(padded),cols)]
    cell_rows=[[Paragraph(c,_ps('sc',fontName='Helvetica',fontSize=8.5,
        textColor=C_DARK_BLUE,alignment=TA_CENTER,leading=12)) for c in row] for row in rows]
    sys_t = _table_box(cell_rows,[CW/cols]*cols,[
        ('BACKGROUND',(0,0),(-1,-1),C_LIGHT_BLUE),
        ('GRID',(0,0),(-1,-1),0.5,C_CODE_BDR),
        ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),
    ])
    story.append(sys_t)
    story.append(Spacer(1,0.25*inch))

    # Stats bar
    stats=[('25','Challenges'),('3','Difficulty Levels'),('20','Sections/Problem'),('500+','Lines of Code')]
    stat_cells=[]
    for val,lbl in stats:
        stat_cells.append(_table_box([
            [Paragraph(f'<b>{val}</b>',_ps('sv',fontName='Helvetica-Bold',fontSize=24,
                textColor=C_DARK_BLUE,alignment=TA_CENTER))],
            [Paragraph(lbl,_ps('sl',fontName='Helvetica',fontSize=9,
                textColor=C_MED_GRAY,alignment=TA_CENTER))],
        ],[CW/4-0.1*inch],[
            ('TOPPADDING',(0,0),(-1,-1),10),('BOTTOMPADDING',(0,0),(-1,-1),10),
        ]))
    stats_t=_table_box([stat_cells],[CW/4]*4,[
        ('BOX',(0,0),(-1,-1),2,C_DARK_BLUE),
        ('LINEBEFORE',(1,0),(3,0),1,C_CODE_BDR),
        ('TOPPADDING',(0,0),(-1,-1),0),('BOTTOMPADDING',(0,0),(-1,-1),0),
        ('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),0),
    ])
    story.append(stats_t)
    return story

# ═══════════════════════════════════════════════════════════════════════════════
# TABLE OF CONTENTS
# ═══════════════════════════════════════════════════════════════════════════════
def build_toc():
    story=[PageBreak()]
    story.append(_table_box([[Paragraph('<b>Table of Contents</b>',
        _ps('toc_main',fontName='Helvetica-Bold',fontSize=20,textColor=white,
        alignment=TA_CENTER,leading=26))]],[CW],[
        ('BACKGROUND',(0,0),(-1,-1),C_DARK_BLUE),
        ('TOPPADDING',(0,0),(-1,-1),12),('BOTTOMPADDING',(0,0),(-1,-1),12),
    ]))
    story.append(Spacer(1,14))

    def toc_row(num,title,concepts,diff):
        dc={'Beginner':C_BEG_DARK,'Intermediate':C_INT_DARK,'Advanced':C_ADV_DARK}
        di={'Beginner':'🟢','Intermediate':'🟡','Advanced':'🔴'}
        num_p  = Paragraph(f'<b>{num}</b>',_ps('tn',fontName='Helvetica-Bold',fontSize=10,
            textColor=dc[diff],alignment=TA_CENTER))
        title_p= Paragraph(f'<b>{title}</b>',_ps('tt',fontName='Helvetica-Bold',fontSize=10,
            textColor=C_DARK_GRAY,alignment=TA_LEFT))
        conc_p = Paragraph(concepts,_ps('tc',fontName='Helvetica',fontSize=8.5,
            textColor=C_MED_GRAY,alignment=TA_LEFT))
        diff_p = Paragraph(f'{di[diff]} {diff}',_ps('td',fontName='Helvetica-Bold',fontSize=8.5,
            textColor=dc[diff],alignment=TA_RIGHT))
        return [num_p,title_p,conc_p,diff_p]

    # Section headers + rows
    def diff_header(label, color):
        p = Paragraph(f'<b>{label}</b>',_ps('dh',fontName='Helvetica-Bold',fontSize=10,
            textColor=white,alignment=TA_LEFT))
        t = _table_box([[p]],[CW],[
            ('BACKGROUND',(0,0),(-1,-1),color),
            ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),
            ('LEFTPADDING',(0,0),(-1,-1),10),
        ])
        return t

    story.append(diff_header('🟢  BEGINNER LEVEL   (Problems 1–7)',C_BEG_DARK))
    beg_rows=[toc_row(p['num'],p['title'],p['concepts'],p['difficulty']) for p in ALL_PROBLEMS if p['difficulty']=='Beginner']
    story.append(_table_box(beg_rows,[0.4*inch,CW*0.35,CW*0.38,1.0*inch],[
        ('GRID',(0,0),(-1,-1),0.3,C_CODE_BDR),
        ('BACKGROUND',(0,0),(-1,-1),C_BEG_LIGHT),
        ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),
        ('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
    ]))
    story.append(Spacer(1,6))

    story.append(diff_header('🟡  INTERMEDIATE LEVEL   (Problems 8–16)',C_INT_DARK))
    int_rows=[toc_row(p['num'],p['title'],p['concepts'],p['difficulty']) for p in ALL_PROBLEMS if p['difficulty']=='Intermediate']
    story.append(_table_box(int_rows,[0.4*inch,CW*0.35,CW*0.38,1.0*inch],[
        ('GRID',(0,0),(-1,-1),0.3,C_CODE_BDR),
        ('BACKGROUND',(0,0),(-1,-1),C_INT_LIGHT),
        ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),
        ('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
    ]))
    story.append(Spacer(1,6))

    story.append(diff_header('🔴  ADVANCED LEVEL   (Problems 17–25)',C_ADV_DARK))
    adv_rows=[toc_row(p['num'],p['title'],p['concepts'],p['difficulty']) for p in ALL_PROBLEMS if p['difficulty']=='Advanced']
    story.append(_table_box(adv_rows,[0.4*inch,CW*0.35,CW*0.38,1.0*inch],[
        ('GRID',(0,0),(-1,-1),0.3,C_CODE_BDR),
        ('BACKGROUND',(0,0),(-1,-1),C_ADV_LIGHT),
        ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),
        ('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
    ]))
    story.append(Spacer(1,10))

    story += h_bar()
    for s in ['📌 Top OOP Interview Patterns','⚠️ Common Python OOP Mistakes','❓ Most Asked OOP Interview Questions']:
        story.append(Paragraph(f'  {s}', ST['toc_h2']))
    return story

# ═══════════════════════════════════════════════════════════════════════════════
# PROBLEM RENDERER
# ═══════════════════════════════════════════════════════════════════════════════
def render_problem(p):
    story = [PageBreak()]
    story += prob_header_row(p['num'],p['title'],p['difficulty'],p['concepts'],p['system'])

    def sec(n,icon,title): return section_hdr(icon,title,n)

    # 1. Problem Statement
    story += sec(1,'📝','Problem Statement')
    story.append(Paragraph(p['statement'], ST['body']))
    story += light_divider()

    # 2. Real-world Scenario
    story += sec(2,'🌍','Real-World Scenario')
    story.append(Paragraph(p['scenario'], ST['body']))
    story += light_divider()

    # 3. Requirements
    story += sec(3,'✅','Requirements / Constraints')
    story += bullet_list(p['requirements'])

    # 4+5. Input/Output Format
    story += sec(4,'📥','Input & Output Format')
    story.append(Paragraph(f'<b>Input:</b>  {p["input_format"]}', ST['body_left']))
    story.append(Paragraph(f'<b>Output:</b> {p["output_format"]}', ST['body_left']))
    story += light_divider()

    # 6. Sample Input
    story += sec(6,'💻','Sample Input')
    story += code_block(p['sample_input'], 'Sample Input')

    # 7. Expected Output
    story += sec(7,'✅','Expected Output')
    story += output_block(p['sample_output'], 'Expected Output')

    # 8. Step-by-Step
    story += sec(8,'🔢','Step-by-Step Explanation')
    story += num_list(p['steps'])

    # 9. Edge Cases
    story += sec(9,'⚠️','Important Edge Cases')
    story += bullet_list(p['edge_cases'])

    # 10. Concepts Tested
    story += sec(10,'🧠','Concepts Tested')
    story += concepts_chips(p['concepts_tested'])

    # 11+12. Complexity
    story += sec(11,'⏱️','Time & Space Complexity')
    story += complexity_table(p['time_complexity'],p['space_complexity'],p['time_note'],p['space_note'])

    # 13. Starter Code
    story += sec(13,'🚀','Starter Code Template')
    story += code_block(p['starter_code'], 'Python — Starter Template (Try it yourself first!)')

    # 14. Full Solution
    story += sec(14,'💡','Full Working Solution')
    story += code_block(p['solution'], 'Python — Complete Solution')

    # 15. Alternate Solution
    if p.get('alt_solution'):
        story += sec(15,'⚡','Alternate / Optimized Solution')
        story += code_block(p['alt_solution'], 'Python — Alternate Approach')

    # 16. Tips & Mistakes
    story += tip_box(p['tips'], '💡 Interview Tips')

    # 17. Dry Run
    story += sec(17,'🔍','Dry Run Example')
    story += code_block(p['dry_run'], 'Execution Trace')

    # 18. Test Cases
    story += sec(18,'🧪','Additional Test Cases')
    story += test_cases_table(p['test_cases'])

    return story

# ═══════════════════════════════════════════════════════════════════════════════
# ADDITIONAL SECTIONS
# ═══════════════════════════════════════════════════════════════════════════════
def build_oop_patterns():
    story = section_banner('Top OOP Interview Patterns','📌')
    story.append(Paragraph(
        'These are the most frequently tested OOP design patterns in technical interviews at '
        'top companies (Google, Amazon, Microsoft, Flipkart, etc.). Master these patterns and '
        'you will confidently handle most OOP design questions.', ST['body']))
    story.append(Spacer(1,10))

    patterns = [
        {
            'name':'1. Singleton Pattern',
            'intent':'Ensure a class has only ONE instance and provide a global access point.',
            'use_cases':['Database connection pool','Logger','Configuration manager','Thread pool'],
            'code':'''\
class DatabaseConnection:
    _instance = None  # class-level single instance

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.connection = "Connected to DB"
            self._initialized = True

# Test: both variables point to the SAME object
db1 = DatabaseConnection()
db2 = DatabaseConnection()
print(db1 is db2)  # True — Singleton guaranteed''',
            'tip':'Thread-safe Singleton needs a Lock around the if-None check.',
        },
        {
            'name':'2. Factory Pattern',
            'intent':'Create objects without specifying the exact class — delegate creation to a factory method.',
            'use_cases':['Vehicle creation','Payment gateway','Notification service','Document generator'],
            'code':'''\
from abc import ABC, abstractmethod

class Notification(ABC):
    @abstractmethod
    def send(self, message: str): pass

class EmailNotification(Notification):
    def send(self, msg): print(f"[EMAIL] {msg}")

class SMSNotification(Notification):
    def send(self, msg): print(f"[SMS] {msg}")

class PushNotification(Notification):
    def send(self, msg): print(f"[PUSH] {msg}")

class NotificationFactory:
    @staticmethod
    def create(ntype: str) -> Notification:
        mapping = {
            "email": EmailNotification,
            "sms":   SMSNotification,
            "push":  PushNotification,
        }
        cls = mapping.get(ntype.lower())
        if not cls: raise ValueError(f"Unknown type: {ntype}")
        return cls()

# Open for extension: add WhatsApp without changing existing code
n = NotificationFactory.create("email")
n.send("Your OTP is 123456")''',
            'tip':'Factory satisfies Open/Closed Principle — add new types without modifying factory.',
        },
        {
            'name':'3. Observer Pattern',
            'intent':'Define a one-to-many dependency so all dependents are notified on state change.',
            'use_cases':['Event systems','Stock price alerts','Social media notifications','GUI events'],
            'code':'''\
from abc import ABC, abstractmethod

class Subject:
    def __init__(self):
        self._observers = []

    def subscribe(self, obs):   self._observers.append(obs)
    def unsubscribe(self, obs): self._observers.remove(obs)
    def notify(self, data):
        for obs in self._observers:
            obs.update(data)

class Observer(ABC):
    @abstractmethod
    def update(self, data): pass

class StockPriceAlertApp(Subject):
    def __init__(self, ticker):
        super().__init__()
        self.ticker = ticker
        self._price = 0

    @property
    def price(self): return self._price

    @price.setter
    def price(self, value):
        self._price = value
        self.notify({"ticker": self.ticker, "price": value})

class InvestorAlert(Observer):
    def __init__(self, name, threshold):
        self.name = name; self.threshold = threshold
    def update(self, data):
        if data["price"] >= self.threshold:
            print(f"[{self.name}] ALERT: {data['ticker']} hit Rs {data['price']}")

stock = StockPriceAlertApp("INFY")
stock.subscribe(InvestorAlert("Alice", 1800))
stock.subscribe(InvestorAlert("Bob",   1900))
stock.price = 1850   # Triggers Alice but not Bob''',
            'tip':'Use @property setter to auto-notify — cleaner than calling notify() manually.',
        },
        {
            'name':'4. Strategy Pattern',
            'intent':'Define a family of algorithms, encapsulate each one, and make them interchangeable.',
            'use_cases':['Payment methods','Sorting algorithms','Compression','Route finding','Pricing'],
            'code':'''\
from abc import ABC, abstractmethod

class PaymentStrategy(ABC):
    @abstractmethod
    def pay(self, amount: float) -> None: pass

class CreditCardPayment(PaymentStrategy):
    def __init__(self, card_no): self.card_no = card_no
    def pay(self, amount): print(f"[CREDIT CARD] Rs {amount:,} charged to {self.card_no[-4:]}")

class UPIPayment(PaymentStrategy):
    def __init__(self, upi_id): self.upi_id = upi_id
    def pay(self, amount): print(f"[UPI] Rs {amount:,} sent via {self.upi_id}")

class NetBankingPayment(PaymentStrategy):
    def pay(self, amount): print(f"[NET BANKING] Rs {amount:,} transferred")

class ShoppingCart:
    def __init__(self): self.total = 0
    def add_item(self, price): self.total += price
    def checkout(self, strategy: PaymentStrategy):
        strategy.pay(self.total)  # Polymorphic — doesn't care WHICH strategy

cart = ShoppingCart()
cart.add_item(999); cart.add_item(1499)
cart.checkout(UPIPayment("alice@paytm"))
cart.checkout(CreditCardPayment("4111111111111234"))  # Same cart, different payment''',
            'tip':'Strategy makes algorithms interchangeable at RUNTIME — key interview differentiator from polymorphism.',
        },
        {
            'name':'5. Decorator Pattern',
            'intent':'Add behaviour to objects dynamically without altering their class.',
            'use_cases':['Coffee shop add-ons','Middleware in web frameworks','Logging wrappers','Caching'],
            'code':'''\
from abc import ABC, abstractmethod

class Coffee(ABC):
    @abstractmethod
    def cost(self) -> float: pass
    @abstractmethod
    def description(self) -> str: pass

class SimpleCoffee(Coffee):
    def cost(self): return 40
    def description(self): return "Plain Coffee"

class CoffeeDecorator(Coffee):
    def __init__(self, coffee: Coffee):
        self._coffee = coffee
    def cost(self): return self._coffee.cost()
    def description(self): return self._coffee.description()

class Milk(CoffeeDecorator):
    def cost(self): return self._coffee.cost() + 15
    def description(self): return self._coffee.description() + ", Milk"

class Sugar(CoffeeDecorator):
    def cost(self): return self._coffee.cost() + 5
    def description(self): return self._coffee.description() + ", Sugar"

class Caramel(CoffeeDecorator):
    def cost(self): return self._coffee.cost() + 30
    def description(self): return self._coffee.description() + ", Caramel"

# Build custom coffee dynamically
my_coffee = Caramel(Milk(Sugar(SimpleCoffee())))
print(my_coffee.description())  # Plain Coffee, Sugar, Milk, Caramel
print(f"Cost: Rs {my_coffee.cost()}")  # 40+5+15+30 = Rs 90''',
            'tip':'Decorator wraps objects in layers — each layer adds responsibility.',
        },
        {
            'name':'6. Command Pattern',
            'intent':'Encapsulate a request as an object — enabling undo, queuing, and logging.',
            'use_cases':['Text editor undo/redo','Smart home automation','Job queue','Transaction log'],
            'code':'''\
# Already covered in Problem 24 (Smart Home).
# Key points to mention in interviews:
# 1. execute() performs the action
# 2. undo() reverses it — store state BEFORE execute
# 3. History as a stack/deque enables undo/redo
# 4. MacroCommand bundles multiple commands into one undoable unit
# 5. Commands can be queued and executed later (job scheduler)''',
            'tip':'Command Pattern = "action as object". Used in Django signals, Celery tasks.',
        },
    ]

    for pat in patterns:
        story.append(Paragraph(pat['name'], ST['h2']))
        story.append(Paragraph(f'<b>Intent:</b> {pat["intent"]}', ST['body_left']))
        story.append(Paragraph('<b>Real-World Use Cases:</b>', ST['h3']))
        story += bullet_list(pat['use_cases'])
        story += code_block(pat['code'], f'Python — {pat["name"]}')
        story += tip_box([pat['tip']], '💡 Pattern Tip')
        story += light_divider()

    return story


def build_common_mistakes():
    story = section_banner('Common Python OOP Mistakes','⚠️')
    story.append(Paragraph(
        'These are the most common Python OOP errors that cause interview failures. '
        'Study each mistake, understand why it happens, and memorise the correct approach.', ST['body']))
    story.append(Spacer(1,10))

    mistakes = [
        {
            'title':'1. Mutable Default Arguments in __init__',
            'wrong':'''\
# WRONG: all instances SHARE the same list!
class Student:
    def __init__(self, name, grades=[]):  # Dangerous!
        self.name   = name
        self.grades = grades  # Same list for every Student!

s1 = Student("Alice")
s2 = Student("Bob")
s1.grades.append(90)
print(s2.grades)  # [90] — BUG! Bob sees Alice's grade!''',
            'right':'''\
# CORRECT: use None as default, create new list in body
class Student:
    def __init__(self, name, grades=None):
        self.name   = name
        self.grades = grades if grades is not None else []

s1 = Student("Alice"); s2 = Student("Bob")
s1.grades.append(90)
print(s2.grades)  # [] — Correct!''',
            'explanation':'Python evaluates default arguments ONCE at function definition time, not each call. Lists, dicts, and sets as defaults are shared across all calls.',
        },
        {
            'title':'2. Forgetting super().__init__() in Subclass',
            'wrong':'''\
class Animal:
    def __init__(self, name):
        self.name = name

class Dog(Animal):
    def __init__(self, name, breed):
        # WRONG: forgot super().__init__(name)
        self.breed = breed  # name attribute never set!

d = Dog("Rex", "Labrador")
print(d.name)  # AttributeError: 'Dog' has no attribute 'name' ''',
            'right':'''\
class Dog(Animal):
    def __init__(self, name, breed):
        super().__init__(name)  # Always call super first!
        self.breed = breed

d = Dog("Rex", "Labrador")
print(d.name)   # Rex
print(d.breed)  # Labrador''',
            'explanation':'Without super().__init__(), the parent class attributes are never initialized. Always call super().__init__() as the FIRST line of the subclass __init__.',
        },
        {
            'title':'3. Using Class Variables as Instance Variables',
            'wrong':'''\
class BankAccount:
    balance = 0  # Class variable — shared by ALL accounts!

    def deposit(self, amount):
        BankAccount.balance += amount  # Changes ALL accounts!

a1 = BankAccount(); a2 = BankAccount()
a1.deposit(1000)
print(a2.balance)  # 1000 — BUG! a2's balance changed!''',
            'right':'''\
class BankAccount:
    def __init__(self, initial=0):
        self.balance = initial  # Instance variable — unique per object

a1 = BankAccount(); a2 = BankAccount()
a1.deposit(1000)
print(a2.balance)  # 0 — Correct!''',
            'explanation':'Class variables are shared across ALL instances. Use instance variables (self.x) for per-object data. Class variables are only appropriate for constants or shared counters.',
        },
        {
            'title':'4. Not Making Abstract Methods Truly Abstract',
            'wrong':'''\
class Shape:
    def area(self):
        pass  # Not enforced — subclass CAN forget to implement it

class Circle(Shape):
    def __init__(self, r): self.r = r
    # Forgot to implement area()! No error raised.

c = Circle(5)
print(c.area())  # None — Silent bug!''',
            'right':'''\
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self) -> float: pass  # MUST be implemented by subclasses

class Circle(Shape):
    # If you forget area(), Python raises TypeError at instantiation!
    def area(self): return 3.14159 * self.r ** 2''',
            'explanation':'Without @abstractmethod, subclasses can silently skip implementing critical methods. Always use ABC + @abstractmethod to enforce the contract.',
        },
        {
            'title':'5. Accessing Private Attributes Directly',
            'wrong':'''\
class Person:
    def __init__(self, name, age):
        self.__age = age  # name-mangled to _Person__age

p = Person("Alice", 25)
print(p.__age)       # AttributeError!
print(p._Person__age)  # Works but WRONG — bypasses encapsulation!''',
            'right':'''\
class Person:
    def __init__(self, name, age):
        self.__age = age

    @property
    def age(self): return self.__age

    @age.setter
    def age(self, value):
        if value < 0: raise ValueError("Age cannot be negative")
        self.__age = value

p = Person("Alice", 25)
print(p.age)   # 25 — Correct way
p.age = 30     # Uses setter with validation''',
            'explanation':'Double underscore triggers name-mangling (__age → _Person__age). Always provide @property and @setter for controlled access to private attributes.',
        },
        {
            'title':'6. Incorrect __eq__ Without __hash__',
            'wrong':'''\
class Point:
    def __init__(self, x, y): self.x=x; self.y=y
    def __eq__(self, other): return self.x==other.x and self.y==other.y
    # Missing __hash__!

p1 = Point(1, 2); p2 = Point(1, 2)
print(p1 == p2)         # True — correct
print(p1 in {p2})       # False! — BUG: default hash differs
# Python sets __hash__=None if __eq__ defined without __hash__''',
            'right':'''\
class Point:
    def __init__(self, x, y): self.x=x; self.y=y
    def __eq__(self, other): return self.x==other.x and self.y==other.y
    def __hash__(self): return hash((self.x, self.y))

p1 = Point(1, 2); p2 = Point(1, 2)
print(p1 == p2)      # True
print(p1 in {p2})    # True — works correctly in sets/dicts''',
            'explanation':'When you override __eq__, Python sets __hash__ to None (making object unhashable). Always define __hash__ alongside __eq__ for objects used in sets or dict keys.',
        },
        {
            'title':'7. Modifying a List While Iterating Over It',
            'wrong':'''\
class Classroom:
    def remove_failing_students(self):
        for student in self.students:       # Iterating
            if student.get_average() < 60:
                self.students.remove(student)  # Modifying during iteration!
        # Skips every other failing student — subtle bug!''',
            'right':'''\
class Classroom:
    def remove_failing_students(self):
        # Method 1: iterate over a copy
        for student in self.students[:]:
            if student.get_average() < 60:
                self.students.remove(student)

        # Method 2: filter (preferred)
        self.students = [s for s in self.students if s.get_average() >= 60]''',
            'explanation':'Removing items from a list while iterating causes skipped elements because list indices shift. Always iterate over a copy or use list comprehension.',
        },
        {
            'title':'8. Not Using super() in Multiple Inheritance',
            'wrong':'''\
class A:
    def __init__(self): print("A init"); self.a = 1

class B(A):
    def __init__(self):
        A.__init__(self)  # Direct call — breaks MRO!
        self.b = 2

class C(A):
    def __init__(self):
        A.__init__(self)  # Direct call — breaks MRO!
        self.c = 3

class D(B, C):
    def __init__(self):
        B.__init__(self)
        C.__init__(self)  # A.__init__ called TWICE!''',
            'right':'''\
class A:
    def __init__(self): print("A init"); self.a = 1

class B(A):
    def __init__(self): super().__init__(); self.b = 2

class C(A):
    def __init__(self): super().__init__(); self.c = 3

class D(B, C):
    def __init__(self): super().__init__(); self.d = 4

# Python MRO ensures A.__init__ is called exactly ONCE
d = D()  # Output: "A init" — only once!''',
            'explanation':'super() follows the MRO (C3 linearisation), ensuring each parent is initialised exactly once. Direct class calls break cooperative multiple inheritance.',
        },
    ]

    for m in mistakes:
        story.append(Paragraph(m['title'], ST['h2']))
        story += code_block(m['wrong'], '❌ WRONG — Common Mistake')
        story += code_block(m['right'], '✅ CORRECT — Proper Approach')
        story += warn_box([m['explanation']], '📖 Why This Happens')
        story += light_divider()

    return story


def build_interview_questions():
    story = section_banner('Most Asked OOP Interview Questions','❓')
    story.append(Paragraph(
        'These questions are asked in interviews at Amazon, Google, Microsoft, Flipkart, '
        'Infosys, TCS, Wipro, and most tech companies. Prepare concise, confident answers '
        'with examples from the 25 problems in this guide.', ST['body']))
    story.append(Spacer(1,10))

    qa_sections = [
        {
            'category': '🔷 Core OOP Concepts',
            'color': C_DARK_BLUE,
            'qas': [
                ("What are the 4 pillars of OOP?",
                 "Encapsulation (hiding data), Abstraction (hiding implementation), "
                 "Inheritance (reusing code), Polymorphism (many forms). "
                 "Example: BankAccount encapsulates _balance; Animal is abstract; "
                 "Dog inherits Animal; speak() is polymorphic."),
                ("Difference between a Class and an Object?",
                 "A Class is a blueprint/template (e.g., BankAccount class). "
                 "An Object is a specific instance (e.g., alice_account = BankAccount('Alice', 1000)). "
                 "Class defines attributes and methods; Object has actual values."),
                ("What is the difference between __init__ and __new__?",
                 "__new__ creates the object (allocates memory) and returns it. "
                 "__init__ initialises the already-created object with attribute values. "
                 "__new__ is used in Singleton pattern and metaclasses."),
                ("What is method overriding vs method overloading?",
                 "Overriding: subclass redefines a method from the parent class (e.g., calculate_pay() in Employee subclasses). "
                 "Overloading: same method name, different parameters — Python achieves this with *args/**kwargs or default params."),
                ("What is the difference between is-a and has-a relationships?",
                 "is-a = Inheritance: Dog IS-A Animal. "
                 "has-a = Composition/Aggregation: Library HAS-A list of Books. "
                 "Prefer composition over inheritance when the relationship is has-a."),
            ]
        },
        {
            'category': '🔷 Encapsulation & Access Modifiers',
            'color': C_ACCENT,
            'qas': [
                ("Explain public, protected, and private in Python.",
                 "Public: name — accessible anywhere. "
                 "Protected: _name — convention-only, accessible but 'please don't'. "
                 "Private: __name — name-mangled to _ClassName__name, harder to access externally. "
                 "Python enforces by convention, not true access control."),
                ("What is name mangling? Give an example.",
                 "Python transforms __attr to _ClassName__attr to make it harder (not impossible) to access from outside. "
                 "Example: BankAccount.__balance becomes BankAccount._BankAccount__balance. "
                 "Access via account._BankAccount__balance still works — it's a hint, not a lock."),
                ("When would you use @property vs a regular method?",
                 "Use @property when: the attribute needs validation on set; it's computed from other attrs; "
                 "you want the caller to use attribute syntax (account.balance) not method syntax (account.get_balance()). "
                 "Regular method is better for actions with side effects (deposit, withdraw)."),
            ]
        },
        {
            'category': '🔷 Inheritance & Polymorphism',
            'color': C_TEAL,
            'qas': [
                ("What is the Method Resolution Order (MRO) in Python?",
                 "MRO is the order Python searches for methods in class hierarchies. "
                 "Python uses C3 linearisation (left-to-right, no class before its parents). "
                 "Check it with ClassName.__mro__ or ClassName.mro(). "
                 "Example: TeachingAssistant(Teacher, Student) → TA → Teacher → Student → Person → object."),
                ("What is the Liskov Substitution Principle?",
                 "Objects of a subclass must be replaceable for objects of the parent class without breaking the program. "
                 "If you have a method that accepts Employee, it must work with FullTimeEmployee and HourlyEmployee too. "
                 "Violation: if a subclass's method raises exceptions the parent's method doesn't."),
                ("Difference between isinstance() and type()?",
                 "isinstance(obj, Class) returns True for the class AND all subclasses (follows inheritance). "
                 "type(obj) == Class is an exact match — doesn't consider subclasses. "
                 "Always prefer isinstance() for OOP checks."),
                ("How does Python achieve polymorphism?",
                 "Through method overriding: different classes implement the same method name differently. "
                 "Duck typing: 'if it walks like a duck and quacks like a duck...' — Python calls .area() on any object "
                 "that has it, regardless of its type. No interface/explicit contract needed."),
            ]
        },
        {
            'category': '🔷 Abstract Classes & Interfaces',
            'color': C_PURPLE,
            'qas': [
                ("Difference between Abstract Class and Interface in Python?",
                 "Python has no formal Interface keyword. Abstract classes (ABC) serve both roles. "
                 "Abstract class: can have implemented methods + abstract methods (partial implementation). "
                 "Interface (Pythonic): ABC with ONLY abstract methods (pure contract). "
                 "Use Protocol (typing) for structural subtyping (duck-typing interface)."),
                ("Can an abstract class have a constructor?",
                 "Yes! Abstract classes CAN have __init__ and implemented methods. "
                 "The key is they CANNOT be instantiated directly. "
                 "Subclasses call super().__init__() to use the parent's constructor. "
                 "Example: Employee(ABC).__init__(name, emp_id) is valid."),
                ("What happens if a subclass doesn't implement all abstract methods?",
                 "Python raises TypeError when you try to instantiate the subclass: "
                 "'Can't instantiate abstract class Dog with abstract method speak'. "
                 "The class definition itself succeeds — the error comes at instantiation."),
            ]
        },
        {
            'category': '🔷 Special / Magic Methods',
            'color': C_PY_BLUE,
            'qas': [
                ("Name 10 important dunder/magic methods in Python.",
                 "__init__(constructor), __str__(string representation), __repr__(debug repr), "
                 "__len__(len(obj)), __eq__(==), __lt__(<), __add__(+), __contains__(in), "
                 "__iter__(for loop), __getitem__(obj[key]). "
                 "Implementing these makes your class integrate seamlessly with Python builtins."),
                ("Difference between __str__ and __repr__?",
                 "__str__: human-readable, used by print() and str(). "
                 "Example: 'BankAccount: Alice, Balance Rs 1000' "
                 "__repr__: developer-focused, used in REPL, should be unambiguous. "
                 "Ideally: eval(repr(obj)) == obj. "
                 "If only __repr__ defined, str() falls back to it."),
                ("How does __eq__ affect object comparison?",
                 "By default, == compares object identity (same as is). "
                 "Override __eq__ to compare by value. "
                 "When you override __eq__, also override __hash__ to maintain consistency "
                 "(objects that compare equal must have the same hash)."),
            ]
        },
        {
            'category': '🔷 Design Patterns & SOLID Principles',
            'color': C_INT_DARK,
            'qas': [
                ("Explain SOLID principles with one-line examples.",
                 "S — Single Responsibility: BankAccount handles only banking, not tax calculations. "
                 "O — Open/Closed: NotificationFactory open to new types (WhatsApp) without changing existing code. "
                 "L — Liskov Substitution: FullTimeEmployee usable wherever Employee is expected. "
                 "I — Interface Segregation: Don't force classes to implement irrelevant methods. "
                 "D — Dependency Inversion: Hotel depends on abstract Room, not concrete StandardRoom."),
                ("When to use composition over inheritance?",
                 "Prefer composition when: the relationship is 'has-a' not 'is-a'; "
                 "you need to change behaviour at runtime (Strategy Pattern); "
                 "inheritance creates tight coupling; the parent class is not stable. "
                 "Example: ShoppingCart HAS-A FareStrategy (not extends it)."),
                ("What is the difference between Aggregation and Composition?",
                 "Composition (strong): child CANNOT exist without parent. "
                 "Example: Heart cannot exist without Body. "
                 "Aggregation (weak): child CAN exist independently. "
                 "Example: Classroom HAS-A Student, but Student exists even without Classroom. "
                 "In Python: Composition — child created inside parent. Aggregation — child passed in."),
            ]
        },
    ]

    for section in qa_sections:
        story.append(_table_box(
            [[Paragraph(f'<b>{section["category"]}</b>',_ps('qcat',fontName='Helvetica-Bold',
                fontSize=11,textColor=white,alignment=TA_LEFT,leading=15))]],[CW],[
            ('BACKGROUND',(0,0),(-1,-1),section['color']),
            ('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),
            ('LEFTPADDING',(0,0),(-1,-1),12),
        ]))

        for q, a in section['qas']:
            # Question row
            q_p = Paragraph(f'<b>Q: {q}</b>', _ps('qp',fontName='Helvetica-Bold',fontSize=10,
                textColor=C_DARK_BLUE,alignment=TA_LEFT,leading=14,spaceAfter=3))
            a_p = Paragraph(f'A: {a}', _ps('ap',fontName='Helvetica',fontSize=9.5,
                textColor=C_DARK_GRAY,alignment=TA_JUSTIFY,leading=14,leftIndent=12))
            qa_t = _table_box([[q_p],[a_p]],[CW],[
                ('BACKGROUND',(0,0),(0,0),C_LIGHT_BLUE),
                ('BACKGROUND',(0,1),(0,1),white),
                ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
                ('LEFTPADDING',(0,0),(-1,-1),10),('RIGHTPADDING',(0,0),(-1,-1),10),
                ('BOX',(0,0),(-1,-1),0.5,C_CODE_BDR),
                ('LINEBELOW',(0,0),(0,0),0.5,C_CODE_BDR),
            ])
            story.append(qa_t)
            story.append(Spacer(1,5))
        story.append(Spacer(1,10))

    # Final closing message
    story += section_banner('Keep Practising — You Got This! 🚀','')
    story.append(Paragraph(
        'Congratulations on completing all 25 Python OOP challenges! '
        'You have covered the full spectrum from basic encapsulation to advanced design patterns. '
        'Here is your final checklist before your next interview:', ST['body']))
    story.append(Spacer(1,10))

    checklist = [
        'Review all 25 problems once more — focus on problems you found difficult.',
        'Practice coding each solution from scratch without looking at the answer.',
        'For every problem, be able to explain the Time and Space complexity.',
        'Know the 6 design patterns in this guide and when to apply each one.',
        'Avoid the 8 common mistakes — review them the day before your interview.',
        'For system design questions: start with classes → relationships → methods → edge cases.',
        'Use Python\'s ABC, @property, @staticmethod, @classmethod confidently.',
        'Always mention SOLID principles when designing classes in interviews.',
        'Practice explaining your code out loud — communication is as important as the code.',
        'Build one of these 25 systems from scratch as a portfolio project.',
    ]
    story += num_list(checklist)

    story.append(Spacer(1,15))
    closing = _table_box([[Paragraph(
        '<b>"The best way to learn OOP is to build things. '
        'Every system you design makes the next one easier."</b>',
        _ps('cl',fontName='Helvetica-Bold',fontSize=12,textColor=white,
        alignment=TA_CENTER,leading=18))]],[CW],[
        ('BACKGROUND',(0,0),(-1,-1),C_DARK_BLUE),
        ('TOPPADDING',(0,0),(-1,-1),16),('BOTTOMPADDING',(0,0),(-1,-1),16),
        ('LEFTPADDING',(0,0),(-1,-1),20),('RIGHTPADDING',(0,0),(-1,-1),20),
    ])
    story.append(closing)

    return story


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN BUILD
# ═══════════════════════════════════════════════════════════════════════════════
def main():
    output_path = './Python_OOP_Interview_Challenges.pdf'
    print("Building PDF…")

    doc   = build_doc(output_path)
    story = []

    print("  Cover page…")
    story += build_cover()

    print("  Table of contents…")
    story += build_toc()

    print("  Rendering 25 problems…")
    for p in ALL_PROBLEMS:
        print(f"    Problem {p['num']:02d}: {p['title']}")
        story += render_problem(p)

    print("  OOP Patterns section…")
    story += build_oop_patterns()

    print("  Common Mistakes section…")
    story += build_common_mistakes()

    print("  Interview Questions section…")
    story += build_interview_questions()

    print("  Building PDF…")
    doc.build(story)
    print(f"Done! PDF saved to: {output_path}")
    return output_path

if __name__ == '__main__':
    main()
