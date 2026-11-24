"""Branded CaseLab AI exports: PDF and OpenDocument Text (.odt)."""
from io import BytesIO
from xml.sax.saxutils import escape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, KeepTogether
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from odf.opendocument import OpenDocumentText
from odf.text import P, H
from odf.style import Style, TextProperties, ParagraphProperties

INK = colors.HexColor('#10263b')
TEAL = colors.HexColor('#24536b')
MUTED = colors.HexColor('#5b6875')


def _content(kind, report, messages):
    if kind == 'transcript':
        groups = [('CLIENT MEETING TRANSCRIPT', [
            (('ALEX MORGAN' if m.get('role') == 'assistant' else 'TRAINEE SOLICITOR'), m.get('content', ''))
            for m in messages
        ])]
    else:
        report = report or {}
        groups = [('FORMATIVE FEEDBACK', [('Overall review', report.get('overall', 'No feedback available.'))])]
        criteria = []
        for c in report.get('criteria', []):
            criteria.append((c.get('name', 'Criterion') + ' — ' + c.get('status', 'Unrated'),
                             c.get('evidence', '') + '\nNext step: ' + c.get('next_step', '')))
        groups.append(('ASSESSMENT CRITERIA', criteria))
        for title, field in [('FACTS ESTABLISHED', 'established'), ('POINTS TO EXPLORE', 'unexplored'), ('SUGGESTED NEXT QUESTIONS', 'suggested_questions')]:
            groups.append((title, [(str(i), item) for i, item in enumerate(report.get(field, []), 1)]))
    return groups


def build_pdf(kind, report, messages):
    """Polished, branded A4 report. All content is derived from the saved transcript/feedback."""
    from pathlib import Path
    from reportlab.platypus import Image, Table, TableStyle, CondPageBreak
    from reportlab.lib.utils import ImageReader
    from reportlab.lib.enums import TA_CENTER
    from xml.sax.saxutils import escape as xml_escape
    stream = BytesIO()
    title = 'Client meeting transcript' if kind == 'transcript' else 'Client meeting performance review'
    base = Path(__file__).resolve().parent
    doc = SimpleDocTemplate(stream, pagesize=A4, leftMargin=43, rightMargin=43,
        topMargin=56, bottomMargin=53, title='CaseLab AI | ' + title,
        author='CaseLab AI · Developed by Wolf Wright', pageCompression=1)
    page_w, page_h = A4
    avail = page_w - 86
    NAVY = colors.HexColor('#10263b')
    OFFWHITE = colors.HexColor('#f8f7f3')
    LINE = colors.HexColor('#dedbd4')
    styles = {
      'eyebrow': ParagraphStyle('new_eyebrow',fontName='Helvetica-Bold',fontSize=8.3,leading=13,textColor=TEAL,spaceAfter=7),
      'title': ParagraphStyle('new_title',fontName='Times-Roman',fontSize=24,leading=28,textColor=NAVY,spaceAfter=6),
      'subtitle': ParagraphStyle('new_subtitle',fontName='Helvetica',fontSize=9,leading=14,textColor=MUTED,spaceAfter=12),
      'heading': ParagraphStyle('new_heading',fontName='Helvetica-Bold',fontSize=11.7,leading=16,textColor=TEAL,spaceBefore=15,spaceAfter=10),
      'body': ParagraphStyle('new_body',fontName='Helvetica',fontSize=9.7,leading=15.2,textColor=NAVY,spaceAfter=7),
      'card': ParagraphStyle('new_card',fontName='Helvetica',fontSize=9.1,leading=14,textColor=NAVY),
      'cardtitle': ParagraphStyle('new_cardtitle',fontName='Helvetica-Bold',fontSize=10.2,leading=15,textColor=NAVY,spaceAfter=7),
      'small': ParagraphStyle('new_small',fontName='Helvetica',fontSize=8.4,leading=12.5,textColor=MUTED),
      'rag': ParagraphStyle('new_rag',fontName='Helvetica-Bold',fontSize=8,leading=10,textColor=NAVY),
    }
    def pp(value,style='body'):
        return Paragraph(xml_escape(str(value or '')).replace('\n','<br/>'),styles[style])
    blocks=[]
    logo=base/'caselab_logo_user_hires.png'
    if not logo.exists(): logo=base/'caselab_logo_user.png'
    if logo.exists():
        img=Image(str(logo),width=209,height=55.4,kind='proportional')
        img.hAlign='LEFT'
        blocks.append(img)
    else:
        blocks.append(Paragraph('CaseLab AI',styles['title']))
    blocks.extend([Spacer(1,11),pp('LEGAL SKILLS  /  INTELLIGENT PRACTICE','eyebrow'),
      pp(title,'title'),pp('Scenario 01  ·  Property practice  ·  Alex Morgan  |  Developed by Wolf Wright','subtitle'),
      HRFlowable(width='100%',thickness=1,color=LINE),Spacer(1,10)])
    if kind=='transcript':
        blocks.append(pp('MEETING RECORD','heading'))
        for i,m in enumerate(messages or [],1):
            who='ALEX MORGAN' if m.get('role')=='assistant' else 'TRAINEE SOLICITOR'
            bg=colors.HexColor('#f2f6f7') if m.get('role')=='assistant' else colors.HexColor('#f8f6f1')
            inner=[pp(f'{i:02d}  ·  {who}','eyebrow'),pp(m.get('content',''),'body')]
            tab=Table([[inner]],colWidths=[avail],hAlign='LEFT')
            tab.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),bg),('BOX',(0,0),(-1,-1),.65,LINE),('LEFTPADDING',(0,0),(-1,-1),13),('RIGHTPADDING',(0,0),(-1,-1),13),('TOPPADDING',(0,0),(-1,-1),10),('BOTTOMPADDING',(0,0),(-1,-1),8)]))
            blocks.extend([tab,Spacer(1,10)])
    else:
        report=report or {}
        advisor=base/'feedback_advisor.png'
        overview=str(report.get('overall') or 'No overall feedback available.')
        if advisor.exists():
            img=Image(str(advisor),width=115,height=128,kind='proportional')
            img.drawWidth=103
            img.drawHeight=128
            img.hAlign='LEFT'
            right=[pp('FORMATIVE FEEDBACK','eyebrow'),pp('Overall review','cardtitle'),pp(overview,'card')]
            intro=Table([[img,right]],colWidths=[122,avail-122],hAlign='LEFT')
            intro.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),OFFWHITE),('BOX',(0,0),(-1,-1),.8,LINE),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),13),('RIGHTPADDING',(0,0),(-1,-1),12),('TOPPADDING',(0,0),(-1,-1),13),('BOTTOMPADDING',(0,0),(-1,-1),12)]))
            blocks.extend([intro,Spacer(1,12),pp('CASELAB AI FEEDBACK ADVISOR  ·  AI-GENERATED FORMATIVE COMMENTARY','small')])
        else:
            blocks.extend([pp('FORMATIVE FEEDBACK','heading'),pp(overview)])
        blocks.append(pp('ASSESSMENT CRITERIA','heading'))
        legend=Table([[pp('STRONG  ·  TARGET MET','rag'),pp('DEVELOPING  ·  PARTIAL','rag'),pp('NOT EVIDENCED  ·  TARGET MISSED','rag')]],colWidths=[avail/3]*3)
        legend.setStyle(TableStyle([('BACKGROUND',(0,0),(0,0),colors.HexColor('#ddefe4')),('BACKGROUND',(1,0),(1,0),colors.HexColor('#fff0d2')),('BACKGROUND',(2,0),(2,0),colors.HexColor('#f8e2df')),('TOPPADDING',(0,0),(-1,-1),9),('BOTTOMPADDING',(0,0),(-1,-1),9),('LEFTPADDING',(0,0),(-1,-1),9)]))
        blocks.extend([legend,Spacer(1,13)])
        definitions={
          'Opening and rapport':'Open professionally, put the client at ease and explain the meeting purpose.',
          'Questioning and follow-up':'Use open and focused questions with relevant follow-up.',
          'Client focus and empathy':'Listen actively, acknowledge concerns and establish priorities.',
          'Fact-finding and clarification':'Gather material facts and separate evidence from assumptions.'
        }
        criteria=report.get('criteria',[])
        if not criteria:blocks.append(pp('No criterion-level feedback available.'))
        for i,c in enumerate(criteria,1):
            name=str(c.get('name','Criterion'))
            status=str(c.get('status','Not evidenced'))
            state=status.lower()
            if state=='strong':status_label='TARGET MET'; col=colors.HexColor('#23845f'); bg=colors.HexColor('#eaf5ef')
            elif state=='developing':status_label='DEVELOPING';col=colors.HexColor('#bb8431');bg=colors.HexColor('#fff3df')
            else:status_label='NOT EVIDENCED';col=colors.HexColor('#b65350');bg=colors.HexColor('#faebea')
            left=[pp(f'CRITERION {i:02d}','eyebrow'),pp(name,'cardtitle'),pp(definitions.get(name,'Demonstrate the relevant interviewing skill.'),'card')]
            right=[pp(status_label,'rag'),Spacer(1,6),pp(c.get('evidence',''),'card'),Spacer(1,8),pp('NEXT STEP','eyebrow'),pp(c.get('next_step',''),'card')]
            row=Table([[left,right]],colWidths=[avail*.40,avail*.60],hAlign='LEFT')
            row.setStyle(TableStyle([('BACKGROUND',(0,0),(0,0),OFFWHITE),('BACKGROUND',(1,0),(1,0),bg),('LINEBEFORE',(1,0),(1,0),3,col),('BOX',(0,0),(-1,-1),.7,LINE),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),13),('RIGHTPADDING',(0,0),(-1,-1),13),('TOPPADDING',(0,0),(-1,-1),13),('BOTTOMPADDING',(0,0),(-1,-1),13)]))
            blocks.extend([row,Spacer(1,10)])
        for title,key,col in [('FACTS ESTABLISHED','established','#26845f'),('POINTS TO EXPLORE','unexplored','#b67e32'),('SUGGESTED NEXT QUESTIONS','suggested_questions','#24536b')]:
            blocks.append(CondPageBreak(75))
            blocks.append(pp(title,'heading'))
            items=report.get(key,[])
            if not items: blocks.append(pp('No points recorded.','small'))
            for i,item in enumerate(items or [],1):
                t=Table([[pp(f'{i:02d}','eyebrow'),pp(item,'card')]],colWidths=[34,avail-34],hAlign='LEFT')
                t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),colors.white),('LINEBEFORE',(0,0),(0,0),2.5,colors.HexColor(col)),('LINEBELOW',(0,0),(-1,-1),.55,LINE),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),9),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]))
                blocks.extend([t,Spacer(1,5)])
        blocks.extend([Spacer(1,14),pp('Formative AI-generated feedback for training. This report is not an official SQE2 assessment or legal advice.','small')])
    def decorate(canvas,doc):
        canvas.saveState()
        canvas.setStrokeColor(LINE);canvas.setLineWidth(.65)
        canvas.line(43,42,page_w-43,42)
        canvas.setFont('Helvetica-Bold',7.2);canvas.setFillColor(TEAL)
        canvas.drawString(43,29,'CASELAB AI  /  LEGAL SKILLS SIMULATION')
        canvas.setFont('Helvetica',7.4);canvas.setFillColor(MUTED)
        canvas.drawRightString(page_w-43,29,'Developed by Wolf Wright     |     %02d'%doc.page)
        canvas.restoreState()
    doc.build(blocks,onFirstPage=decorate,onLaterPages=decorate)
    return stream.getvalue()


def build_odt(kind, report, messages):
    title = 'Client meeting transcript' if kind == 'transcript' else 'Client meeting performance review'
    doc = OpenDocumentText()
    heading_style = Style(name='CLHeading', family='paragraph')
    heading_style.addElement(TextProperties(fontfamily='Liberation Serif', fontsize='22pt', color='#10263b', fontweight='bold'))
    doc.styles.addElement(heading_style)
    section_style = Style(name='CLSection', family='paragraph')
    section_style.addElement(TextProperties(fontfamily='Liberation Sans', fontsize='13pt', color='#24536b', fontweight='bold'))
    section_style.addElement(ParagraphProperties(margintop='0.25in', marginbottom='0.09in'))
    doc.styles.addElement(section_style)
    label_style = Style(name='CLLabel', family='paragraph')
    label_style.addElement(TextProperties(fontfamily='Liberation Sans', fontsize='10pt', color='#10263b', fontweight='bold'))
    doc.styles.addElement(label_style)
    body_style = Style(name='CLBody', family='paragraph')
    body_style.addElement(TextProperties(fontfamily='Liberation Sans', fontsize='10pt', color='#263e4d'))
    body_style.addElement(ParagraphProperties(marginbottom='0.12in'))
    doc.styles.addElement(body_style)
    doc.text.addElement(H(outlinelevel=1, stylename=heading_style, text='CaseLab AI'))
    doc.text.addElement(P(stylename=body_style, text=f'{title}  |  Developed by Wolf Wright'))
    for section, entries in _content(kind, report, messages):
        doc.text.addElement(H(outlinelevel=2, stylename=section_style, text=section))
        for heading, body in entries:
            doc.text.addElement(P(stylename=label_style, text=str(heading)))
            doc.text.addElement(P(stylename=body_style, text=str(body or '')))
    output = BytesIO()
    doc.save(output)
    return output.getvalue()
