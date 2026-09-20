from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, PageBreak,
                                 Table, TableStyle, HRFlowable)
from pathlib import Path
import datetime

OUT = Path(r"C:\Users\Harsh\Downloads\AI-Query-Optimizer\AI-Query-Optimizer-main\AI-Query-Optimizer-Beginner-Guide.pdf")
OUT.parent.mkdir(parents=True, exist_ok=True)

NAVY   = colors.HexColor('#0B1F47')
BLUE   = colors.HexColor('#2457F5')
LBLUE  = colors.HexColor('#EEF3FF')
TEAL   = colors.HexColor('#0D9488')
LTEAL  = colors.HexColor('#ECFDF5')
AMBER  = colors.HexColor('#B45309')
LAMBER = colors.HexColor('#FFFBEB')
RED    = colors.HexColor('#B91C1C')
LRED   = colors.HexColor('#FEF2F2')
INK    = colors.HexColor('#172033')
MUTED  = colors.HexColor('#5A6A85')
LGRAY  = colors.HexColor('#F4F6FB')
BORDER = colors.HexColor('#CBD5E1')
WHITE  = colors.white

W, H = A4
SS = getSampleStyleSheet()

def add(name, **kw): SS.add(ParagraphStyle(name=name, **kw))

add('Cover1',    fontName='Helvetica-Bold', fontSize=28, leading=34, textColor=WHITE, alignment=TA_CENTER, spaceAfter=10)
add('Cover2',    fontName='Helvetica-Bold', fontSize=13, leading=17, textColor=colors.HexColor('#B8C9F0'), alignment=TA_CENTER, spaceAfter=6)
add('Cover3',    fontName='Helvetica',      fontSize=9.5, leading=13.5, textColor=colors.HexColor('#8FA3CC'), alignment=TA_CENTER)
add('TOCItem',   fontName='Helvetica',      fontSize=8.5, leading=13, textColor=INK)
add('Chapter',   fontName='Helvetica-Bold', fontSize=14, leading=18, textColor=WHITE, spaceAfter=0)
add('H2',        fontName='Helvetica-Bold', fontSize=11, leading=15, textColor=NAVY, spaceBefore=8, spaceAfter=4)
add('H3',        fontName='Helvetica-Bold', fontSize=9.5, leading=13, textColor=BLUE, spaceBefore=6, spaceAfter=3)
add('Body',      fontName='Helvetica',      fontSize=8.5, leading=13, textColor=INK, spaceAfter=4, alignment=TA_JUSTIFY)
add('BulletItem',fontName='Helvetica',      fontSize=8.5, leading=12.5, textColor=INK, spaceAfter=2.5, leftIndent=10)
add('SmallB',    fontName='Helvetica-Bold', fontSize=7.5, leading=10, textColor=INK)
add('TH',        fontName='Helvetica-Bold', fontSize=8, leading=11, textColor=WHITE)
add('TD',        fontName='Helvetica',      fontSize=7.5, leading=11, textColor=INK)
add('Callout',   fontName='Helvetica',      fontSize=8.5, leading=12.5, textColor=NAVY, spaceAfter=4, spaceBefore=3)
add('CalloutB',  fontName='Helvetica-Bold', fontSize=8.5, leading=12.5, textColor=NAVY, spaceAfter=2, spaceBefore=3)

def S(txt, style='Body'): return Paragraph(txt, SS[style])
def HR(color=BORDER, thickness=0.5): return HRFlowable(width='100%', thickness=thickness, color=color, spaceAfter=4, spaceBefore=2)
def SP(h=4): return Spacer(1, h)

def bullets(items, style='BulletItem'):
    return [Paragraph(f'<bullet>&bull;</bullet> {item}', SS[style]) for item in items]

def callout(title, body, bg=LBLUE, bc=BLUE):
    data = [[Paragraph(f'<b>{title}</b>', SS['CalloutB'])], [Paragraph(body, SS['Callout'])]]
    t = Table(data, colWidths=[W - 60*mm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), bg),
        ('LINEAFTER',  (0,0), (0,-1), 3, bc),
        ('LINEBEFORE', (0,0), (0,-1), 3, bc),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING',(0,0),(-1,-1), 5),
        ('LEFTPADDING',(0,0),(-1,-1), 7),
        ('RIGHTPADDING',(0,0),(-1,-1), 7),
        ('GRID',(0,0),(-1,-1), 0.3, bc),
    ]))
    return [SP(2), t, SP(4)]

def success(text): return callout('Key Point', text, LTEAL, TEAL)
def warning(text): return callout('Important', text, LRED, RED)

def mktable(rows, widths, header=True):
    data = [[Paragraph(cell, SS['TH' if (i == 0 and header) else 'TD']) for cell in row] for i, row in enumerate(rows)]
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0, hAlign='LEFT')
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0 if header else -1), NAVY),
        ('TEXTCOLOR',(0,0),(-1,0 if header else -1), WHITE),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('GRID',(0,0),(-1,-1), 0.35, BORDER),
        ('ROWBACKGROUNDS',(0, 1 if header else 0),(-1,-1),[WHITE, LGRAY]),
        ('LEFTPADDING',(0,0),(-1,-1), 4),
        ('RIGHTPADDING',(0,0),(-1,-1), 4),
        ('TOPPADDING',(0,0),(-1,-1), 3),
        ('BOTTOMPADDING',(0,0),(-1,-1), 3),
    ]))
    return t

def chapter_block(num, title, subtitle=''):
    data = [[Paragraph(
        f'<b>{num}. {title}</b><br/><font color="#B8C9F0" size="9">{subtitle}</font>',
        SS['Chapter']
    )]]
    t = Table(data, colWidths=[W - 60*mm])
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1), NAVY),
        ('TOPPADDING',(0,0),(-1,-1), 8),
        ('BOTTOMPADDING',(0,0),(-1,-1), 8),
        ('LEFTPADDING',(0,0),(-1,-1), 10),
        ('RIGHTPADDING',(0,0),(-1,-1), 8),
    ]))
    return [SP(8), t, SP(6)]

def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(BORDER)
    canvas.setLineWidth(0.5)
    canvas.line(30, 25, W - 30, 25)
    canvas.setFont('Helvetica', 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(30, 15, 'AI Query Optimizer - Beginner Project Guide')
    canvas.drawCentredString(W/2, 15, datetime.date.today().strftime('%B %Y'))
    canvas.drawRightString(W - 30, 15, f'Page {doc.page}')
    canvas.restoreState()

def cover_page(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, W, H, fill=1, stroke=0)
    canvas.setFillColor(BLUE)
    canvas.rect(0, H*0.55, W, H*0.45, fill=1, stroke=0)
    canvas.setFillColor(colors.HexColor('#0B1F47'))
    canvas.rect(0, 0, W, 50, fill=1, stroke=0)
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(colors.HexColor('#8FA3CC'))
    canvas.drawString(30, 20, 'Comprehensive Beginner Guide - Everything You Need to Understand, Explain, and Defend')
    canvas.drawRightString(W-30, 20, datetime.date.today().strftime('%d %B %Y'))
    canvas.restoreState()

story = []
story += [SP(100), S('AI Query Optimizer', 'Cover1'), SP(8), S('Beginner Project Guide', 'Cover2'), SP(12), S('Machine Learning * LLM * PostgreSQL * Streamlit', 'Cover3'), SP(4), S('Understand - Explain - Defend', 'Cover3'), SP(250)]

story.append(PageBreak())
story += [S('Table of Contents', 'H2'), HR(NAVY, 1.2), SP(6)]
toc_items = [
    ('1', 'What is this Project?', 'The core idea in plain English'),
    ('2', 'Real-World Problem & Why It Matters', 'Why slow queries happen'),
    ('3', 'Objective & Scope', 'What the app does and does not do'),
    ('4', 'Technology Stack', 'Every tool explained simply'),
    ('5', 'Why These Technologies?', 'Choices and trade-offs'),
    ('6', 'System Architecture', 'How all pieces connect'),
    ('7', 'Feature-by-Feature Walkthrough', 'Every screen and function'),
    ('8', 'End-to-End Workflow', 'Step-by-step from input to output'),
    ('9', 'Data, Model & Files', 'What files do what'),
    ('10', 'Security & Responsible Design', 'Why it is built safely'),
    ('11', 'Deployment Guide', 'Local and Streamlit Cloud'),
    ('12', 'Challenges & How They Were Solved', 'Engineering decisions'),
    ('13', 'Limitations - Be Honest', 'What the project cannot do'),
    ('14', 'Future Improvements', 'What could be added next'),
    ('15', 'How to Explain in an Interview', '30-sec and 90-sec answers'),
    ('16', 'Counter Questions & Answers', '25 tough questions'),
    ('17', 'Glossary', 'All terms explained simply'),
]
for num, title, sub in toc_items:
    row_data = [[Paragraph(f'<b>{num}.</b>', SS['TOCItem']), Paragraph(f'<b>{title}</b>  <font color="#8FA3CC" size="8">{sub}</font>', SS['TOCItem'])]]
    rt = Table(row_data, colWidths=[18, W - 60*mm - 18])
    rt.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'), ('LEFTPADDING',(0,0),(-1,-1),0), ('RIGHTPADDING',(0,0),(-1,-1),0), ('TOPPADDING',(0,0),(-1,-1),2), ('BOTTOMPADDING',(0,0),(-1,-1),2)]))
    story.append(rt)
    story.append(HRFlowable(width='100%', thickness=0.3, color=BORDER, spaceAfter=0, spaceBefore=0))

story.append(PageBreak())
story += chapter_block('1', 'What Is This Project?', 'The core idea in plain English')
story += [
    S('Imagine you run a shop with a million product records. You ask the database: "Show me all red shoes under Rs. 2000." The database does not just blindly read every row. It first makes a <b>plan</b> - a recipe - for how to find the answer as efficiently as possible.'),
    S('This project is a <b>dashboard</b> that lets you look inside that plan, understand it, and get guidance on whether anything looks suspicious or slow. Think of it as an X-ray machine for your SQL query - it shows you what is happening under the hood.'),
]
story += success('One-line summary: AI Query Optimizer reads PostgreSQL execution plans, compares row estimates using a trained ML model, and gives beginners clear, safe guidance - all in a visual web app.')
story += [
    S('What is a Query Plan?', 'H2'),
    S('When you send SQL to PostgreSQL, the database engine does not just run it immediately. It first plans how to answer it. The plan includes steps (called <b>Plan Nodes</b>) such as scanning a table, filtering rows, joining tables, and sorting.'),
]
story += bullets([
    'Scan this table (check every row or use an index shortcut).',
    'Filter rows matching the WHERE condition.',
    'Join results from two or more tables.',
    'Sort the final result.',
    'Return a limited number of rows (LIMIT).',
])

story.append(PageBreak())
story += chapter_block('2', 'Real-World Problem and Why It Matters', 'Why slow queries happen')
story += [
    S('The Problem: Estimate Errors', 'H2'),
    S('PostgreSQL uses statistics to estimate how many rows each plan node will return. When these estimates are inaccurate (e.g. data grown significantly, skewed data, or combined filters), PostgreSQL can pick a bad plan.'),
]
story.append(mktable([
    ['Situation', 'Bad Estimate Effect', 'Real Impact'],
    ['Join estimated 10 rows, actual 100,000', 'PostgreSQL picks Nested Loop', 'Millions of comparisons instead of thousands'],
    ['Filter estimated 50%, actual 1%', 'No index is used', 'Full table scan on 10 million rows'],
    ['Sort estimated small, actual huge', 'Too little memory allocated', 'Disk spill, very slow sort'],
], [40*mm, 50*mm, 60*mm]))

story.append(PageBreak())
story += chapter_block('3', 'Objective and Scope', 'What the app does and does not do')
story.append(mktable([
    ['This project IS', 'This project IS NOT'],
    ['An explainability and learning assistant', 'A production-grade autonomous optimizer'],
    ['A visual comparison of ML vs PostgreSQL estimates', 'A replacement for PostgreSQL query planner'],
    ['A safe recommendation system', 'A system that automatically creates indexes'],
    ['A beginner-friendly starting point for diagnostics', 'A universal model for all databases'],
    ['A Streamlit web app deployable on the cloud', 'An enterprise SaaS product'],
], [75*mm, 75*mm]))

story.append(PageBreak())
story += chapter_block('4', 'Technology Stack', 'Every tool explained simply')
techs = [
    ('Python 3', 'The core programming language used.', 'Huge ecosystem for ML, data manipulation, and Web apps.'),
    ('Streamlit', 'Interactive web application framework.', 'Pure Python UI creation without frontend code.'),
    ('PostgreSQL', 'Relational database engine analyzed.', 'Provides structured EXPLAIN JSON execution plans.'),
    ('XGBoost', 'Machine learning model predicting row counts.', 'Gradient boosting excels on structured tabular plan features.'),
    ('scikit-learn & joblib', 'ML preprocessing and serialization.', 'Prepares data and saves trained models to disk (.pkl).'),
    ('Pandas & NumPy', 'DataFrames and numeric processing.', 'Calculates Q-error and parses plan nodes efficiently.'),
    ('Plotly', 'Interactive data visualization.', 'Renders hoverable charts directly in Streamlit.'),
    ('Google Gemini API', 'LLM for English-to-SQL & Query Doctor.', 'Provides plain-English interpretations and explanations.'),
    ('Neon & Streamlit Cloud', 'Cloud database and hosting.', 'Enables public deployment without local machine dependencies.'),
]
for n, w, y in techs:
    story += [S(n, 'H3'), S(f'<b>What:</b> {w}'), S(f'<b>Why:</b> {y}'), HR()]

story.append(PageBreak())
story += chapter_block('5', 'System Architecture', 'How all pieces connect')
story.append(mktable([
    ['Layer', 'What it does', 'Technologies'],
    ['Presentation', 'User interface & controls', 'Streamlit, Plotly'],
    ['Validation', 'Read-only SELECT filter & SQL extraction', 'Python Regex'],
    ['Database', 'Execute EXPLAIN (ANALYZE, FORMAT JSON)', 'psycopg2, PostgreSQL'],
    ['ML Engine', 'Cardinality prediction via XGBoost', 'XGBoost, joblib'],
    ['AI Doctor', 'Plain-English plan diagnosis', 'Google Gemini API'],
    ['Logging', 'Session event logging', 'Python Session State / SQLite'],
], [30*mm, 70*mm, 50*mm]))

story.append(PageBreak())
story += chapter_block('6', 'Feature-by-Feature Walkthrough', 'Every screen and function')
features = [
    ('Upload Plan Mode', 'Parse and analyze EXPLAIN ANALYZE JSON files offline without any database connection.'),
    ('Live Query Mode', 'Connect to PostgreSQL, execute queries safely, and visualize live plan performance.'),
    ('Natural Language to SQL', 'Convert plain English prompts to SQL using Gemini or fast offline matching.'),
    ('ML Cardinality Comparison', 'Compare PostgreSQL estimates vs actual rows vs XGBoost predictions per node.'),
    ('AI Query Doctor', 'Get automated risk ratings, detected anti-patterns, and actionable optimization advice.'),
    ('Smart Index Advisor', 'Rule-based index suggestions for unindexed sequential scans.'),
    ('Activity Logs & Sample Analysis', 'Inspect session activity and run built-in demonstration plans instantly.'),
]
for f, d in features: story += [S(f, 'H2'), S(d), HR()]

story.append(PageBreak())
story += chapter_block('7', 'How to Explain in an Interview', '30-sec and 90-sec answers')
story += callout('30-Second Summary',
    'AI Query Optimizer is a Streamlit dashboard that makes PostgreSQL execution plans understandable. '
    'It uses EXPLAIN ANALYZE JSON to get real plan data, an XGBoost model to predict node cardinality, '
    'and Q-error to compare the model against PostgreSQL estimates. Gemini provides optional plain-English advice. '
    'It is safe by design: read-only SELECT queries only, with zero auto-execution of database changes.')

story += callout('90-Second Summary',
    'A slow SQL query is hard to debug because database planners make row-count estimates at nested steps. '
    'When those estimates fail, PostgreSQL picks inefficient join algorithms or table scans. '
    'My app flattens execution plan nodes and evaluates PostgreSQL estimates, actual rows, and XGBoost predictions using Q-error. '
    'The user sees exact bottlenecks visually via Plotly charts, receives rule-based index recommendations, '
    'and gets Gemini AI summaries. Security is enforced with single SELECT validation, secret management, '
    'and strictly informational advice rather than autonomous database modifications.')

story.append(PageBreak())
story += chapter_block('8', 'Counter Questions & Answers', 'Essential interview prep')
qas = [
    ('What is Q-error?', 'A symmetric ratio metric: max(estimate/actual, actual/estimate). 1.0 is perfect accuracy.'),
    ('Why XGBoost over Neural Networks?', 'Tabular plan features perform better and train faster on tree-based models like XGBoost, which are also easier to explain.'),
    ('Does Gemini train the ML model?', 'No. Gemini provides language translation and text summaries. XGBoost handles numerical cardinality predictions.'),
    ('Why EXPLAIN ANALYZE?', 'EXPLAIN gives estimates only. ANALYZE runs the query to capture actual row counts needed to compute Q-error.'),
    ('How is SQL execution kept safe?', 'Regex extracts pure SQL, validates it as a single SELECT statement, and blocks DDL/DML keywords.'),
]
for q, a in qas: story += [S(f'<b>Q: {q}</b>', 'H3'), S(a), HR()]

story.append(PageBreak())
story += chapter_block('9', 'Glossary', 'Terms in plain English')
glossary = [
    ('Cardinality', 'The number of rows returned by a query operation.'),
    ('Seq Scan', 'Scanning every row in a table sequentially.'),
    ('Index Scan', 'Using an index tree to jump directly to matching rows.'),
    ('Hash Join', 'A join method that builds a hash table of one relation to match another.'),
    ('Q-error', 'Ratio metric measuring estimate accuracy relative to actual rows.'),
    ('Streamlit', 'Python framework for building interactive data web applications.'),
]
story.append(mktable([['Term', 'Definition']] + [[t, d] for t, d in glossary], [40*mm, 110*mm]))

story.append(PageBreak())
story += chapter_block('10', 'Deployment Guide', 'A beginner-safe guide for the live hosted application')
story += callout('Repository roles',
    'The original shared repository is <b>Oxide06/AI-Query-Optimizer</b>. '
    'The personal fork is <b>Harshit-Kumar-1710/AI-Query-Optimizer</b>. '
    'A fork is your copy of a repository: make and test changes in the fork, then open a Pull Request to the original repository when the team wants to merge them.')

story += [S('A. Keep secrets out of GitHub', 'H2')] + bullets([
    'Never paste an API key, database password, or full Neon connection string into app.py, README screenshots, commits, or chat messages.',
    'Keep .env, .streamlit/secrets.toml, .gemini_key.json, and *.db files ignored by Git. The project .gitignore is the safety net, but you must still check git status before pushing.',
    'Use Streamlit Secrets for the deployed app. Use environment variables or a local .env file only for local development.'
])

story += [S('B. Deploy to Streamlit Community Cloud - step by step', 'H2')] + bullets([
    'Push the tested code to GitHub. For the shared version, use the original repository; for personal testing, use the fork.',
    'Open share.streamlit.io, sign in with GitHub, click Create app, and select the repository and the main branch.',
    'Set the main file path to app.py. Streamlit reads requirements.txt and installs the Python packages automatically.',
    'Open App settings, then Secrets. Paste the secret template below after replacing every placeholder. Save it and choose Reboot app.',
    'First test Sample Analysis and Upload Plan. These should work without any live database. Then test Fast Offline Mode. Finally test Live Query after the hosted PostgreSQL secrets are correct.',
    'If requirements.txt changes, redeploy or reboot so Streamlit installs the updated packages.'
])

story += [S('C. Streamlit Secrets template', 'H2'), S('<font name="Courier">GEMINI_API_KEY = "your_key_from_google_ai_studio"<br/>GEMINI_MODEL = "gemini-2.5-flash"<br/>DB_HOST = "your-neon-host.neon.tech"<br/>DB_PORT = "5432"<br/>DB_NAME = "neondb"<br/>DB_USER = "your_database_user"<br/>DB_PASSWORD = "your_database_password"<br/>DB_SSLMODE = "require"</font>', 'Body')]

story += [S('D. Create the correct Gemini key', 'H2')] + bullets([
    'Open Google AI Studio and create or copy a Gemini API key for your project. Store that value as GEMINI_API_KEY in Streamlit Secrets.',
    'Do not use a Google browser login token, a value beginning with Bearer, or an OAuth access token. Those are different credentials and will fail with ACCESS_TOKEN_TYPE_UNSUPPORTED.',
    'After changing the secret, save it and reboot the Streamlit app. The sidebar should say that the Gemini key is active. Use Fast Offline Mode while testing database features without Gemini.'
])

story += [S('E. Configure Neon or another hosted PostgreSQL database', 'H2')] + bullets([
    'Copy the host, database, user, password, and port from the provider dashboard. Do not use localhost in a cloud deployment because localhost means the Streamlit container itself, not your computer.',
    'For Neon, Supabase, Aiven, and most managed PostgreSQL providers, set DB_SSLMODE to require. The app now passes both DB_PORT and DB_SSLMODE to psycopg2.',
    'Create a read-only database user for the demo whenever possible. The app validates SELECT queries, but database permissions are the final protection.',
    'Load the dvd_rental schema/data into the hosted database if you want the built-in sample SQL queries to run. Otherwise use Upload Plan and Sample Analysis for a database-free demo.'
])

story += [S('F. Error checklist', 'H2')]
story.append(mktable([
    ['What you see', 'Likely cause', 'Simple fix'],
    ['ACCESS_TOKEN_TYPE_UNSUPPORTED', 'OAuth/login token was saved as GEMINI_API_KEY.', 'Replace it with a Gemini API key from Google AI Studio and reboot.'],
    ['password authentication failed', 'Database user/password is wrong.', 'Copy both values again from the database provider and update Secrets.'],
    ['SSL connection required', 'Managed database requires encrypted transport.', 'Set DB_SSLMODE = "require".'],
    ['connection timeout / could not connect', 'Wrong host/port or database network is unavailable.', 'Use the provider host, correct port, then test provider status. Do not use localhost on Streamlit Cloud.'],
    ['model/API error', 'Package or selected model is unavailable, quota is exhausted, or key lacks access.', 'Keep google-genai in requirements.txt, use GEMINI_MODEL = "gemini-2.5-flash", check key/quota, and reboot.'],
    ['Only one read-only SELECT allowed', 'The input contains a write statement, multiple statements, or comments.', 'Submit one plain SELECT query only.']
], [42*mm, 52*mm, 56*mm]))

story += success('Deployment order to remember: 1) push code, 2) deploy app, 3) add secrets, 4) reboot, 5) test offline features, 6) test Gemini, 7) test hosted database, 8) confirm Activity Logs do not expose secrets.')

doc = SimpleDocTemplate(
    str(OUT), pagesize=A4, rightMargin=30, leftMargin=30, topMargin=35, bottomMargin=35,
    title='AI Query Optimizer Guide', author='Antigravity'
)
doc.build(story, onFirstPage=cover_page, onLaterPages=footer)
print('PDF generated successfully:', OUT)
