import os
import sys
import subprocess

# Ensure reportlab is installed
try:
    import reportlab
except ImportError:
    print("[INFO] reportlab is not installed. Installing it via pip...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "reportlab"])
    import reportlab

from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# Widescreen presentation size (16:9 ratio)
SLIDE_WIDTH = 960
SLIDE_HEIGHT = 540

def draw_cover(canvas, doc):
    canvas.saveState()
    # Dark slate premium background
    canvas.setFillColor(colors.HexColor("#0f172a"))
    canvas.rect(0, 0, SLIDE_WIDTH, SLIDE_HEIGHT, fill=1, stroke=0)
    # Emerald green accent strip at the bottom
    canvas.setFillColor(colors.HexColor("#10b981"))
    canvas.rect(0, 0, SLIDE_WIDTH, 8, fill=1, stroke=0)
    # Indigo accent strip on the left
    canvas.setFillColor(colors.HexColor("#4f46e5"))
    canvas.rect(0, 0, 16, SLIDE_HEIGHT, fill=1, stroke=0)
    canvas.restoreState()

def draw_slide(canvas, doc):
    canvas.saveState()
    # Soft clean layout background
    canvas.setFillColor(colors.HexColor("#f8fafc"))
    canvas.rect(0, 0, SLIDE_WIDTH, SLIDE_HEIGHT, fill=1, stroke=0)
    
    # Top Indigo Header Banner
    canvas.setFillColor(colors.HexColor("#4f46e5"))
    canvas.rect(0, 490, SLIDE_WIDTH, 50, fill=1, stroke=0)
    
    # Banner Title Text
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 14)
    canvas.drawString(30, 508, "AgriGuard Crop Diagnostics & Smart Farming System")
    
    # Bottom Footer Bar
    canvas.setStrokeColor(colors.HexColor("#cbd5e1"))
    canvas.setLineWidth(0.5)
    canvas.line(30, 35, SLIDE_WIDTH - 30, 35)
    
    canvas.setFillColor(colors.HexColor("#64748b"))
    canvas.setFont("Helvetica", 9)
    canvas.drawString(30, 18, "AgriGuard Technical Presentation Deck")
    canvas.drawRightString(SLIDE_WIDTH - 30, 18, f"Slide {canvas._pageNumber}")
    canvas.restoreState()

def make_presentation_pdf(filename="AgriGuard_Project_Documentation.pdf"):
    styles = getSampleStyleSheet()
    
    # Presentation Palette
    c_primary = colors.HexColor("#4f46e5")    # Indigo
    c_secondary = colors.HexColor("#10b981")  # Emerald
    c_dark = colors.HexColor("#0f172a")       # Slate-900
    c_text = colors.HexColor("#334155")       # Slate-700
    c_white = colors.white
    c_light = colors.HexColor("#f1f5f9")      # Slate-100
    
    # Custom Presentation Text Styles
    cover_title_style = ParagraphStyle(
        "CoverTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=30,
        leading=36,
        textColor=c_white,
        alignment=0,
        spaceAfter=15
    )
    
    cover_subtitle_style = ParagraphStyle(
        "CoverSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=14,
        leading=18,
        textColor=c_secondary,
        spaceAfter=40
    )
    
    cover_meta_style = ParagraphStyle(
        "CoverMeta",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#94a3b8")
    )
    
    slide_title_style = ParagraphStyle(
        "SlideTitle",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=c_primary,
        spaceBefore=0,
        spaceAfter=15,
        keepWithNext=True
    )
    
    slide_subtitle_style = ParagraphStyle(
        "SlideSubtitle",
        parent=styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=c_secondary,
        spaceBefore=8,
        spaceAfter=6,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        "SlideBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14.5,
        textColor=c_text,
        spaceAfter=8
    )

    bullet_style = ParagraphStyle(
        "SlideBullet",
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=6
    )

    code_style = ParagraphStyle(
        "SlideCode",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#0f172a"),
        backColor=c_light,
        borderPadding=6,
        spaceAfter=6
    )

    doc = SimpleDocTemplate(
        filename,
        pagesize=(SLIDE_WIDTH, SLIDE_HEIGHT),
        rightMargin=40,
        leftMargin=40,
        topMargin=75,
        bottomMargin=55
    )
    
    story = []
    
    # ==================== SLIDE 1: COVER SLIDE ====================
    story.append(Spacer(1, 80))
    story.append(Paragraph("AgriGuard: Model Development Journey", cover_title_style))
    story.append(Paragraph("Technical Report on Phases 1-5: Environment, Preprocessing, Architecture, Debugging & Validation", cover_subtitle_style))
    story.append(Spacer(1, 60))
    
    meta_text = (
        "<b>Project Development Presentation Deck</b><br/>"
        "Prepared By: Navin badode and AI Assistant<br/>"
        "Focus: Local CNN Pipeline, Double-Preprocessing Bug Diagnostics, SQLite Log & Dynamic Advisory"
    )
    story.append(Paragraph(meta_text, cover_meta_style))
    story.append(PageBreak())
    
    # ==================== SLIDE 2: DEVELOPMENT PHASES OVERVIEW ====================
    story.append(Paragraph("Development Phases Overview", slide_title_style))
    story.append(Paragraph("The development lifecycle of the complete AgriGuard platform spans 10 distinct phases:", body_style))
    story.append(Spacer(1, 8))

    phases_data = [
        [Paragraph("<b>Phase</b>", body_style), Paragraph("<b>Phase Name</b>", body_style), Paragraph("<b>Key Milestones & Achievements</b>", body_style)],
        [
            Paragraph("Phase 1", body_style),
            Paragraph("Environment Setup", body_style),
            Paragraph("Resolved TensorFlow, NumPy, and h5py library compatibility issues in a clean environment.", body_style)
        ],
        [
            Paragraph("Phase 2", body_style),
            Paragraph("Dataset Preparation", body_style),
            Paragraph("Selected 15 PlantVillage categories (Tomato, Potato, Pepper classes).", body_style)
        ],
        [
            Paragraph("Phase 3", body_style),
            Paragraph("Dataset Verification", body_style),
            Paragraph("Resolved nested folders, generated statistics (20,638 images), and implemented TF dataloaders.", body_style)
        ],
        [
            Paragraph("Phase 4", body_style),
            Paragraph("Model Training", body_style),
            Paragraph("Built a MobileNetV2 transfer learning model with data augmentation and a Dropout(0.3) head.", body_style)
        ],
        [
            Paragraph("Phase 5", body_style),
            Paragraph("Prediction System", body_style),
            Paragraph("Resolved a double preprocessing inference bug that caused inaccurate blight classifications.", body_style)
        ],
        [
            Paragraph("Phase 6", body_style),
            Paragraph("Web Routing & Control", body_style),
            Paragraph("Developed Flask web endpoints for user logins, image uploads, history scans, and bot dialogs.", body_style)
        ],
        [
            Paragraph("Phase 7", body_style),
            Paragraph("Database Persistence", body_style),
            Paragraph("Structured SQLite schemas for user credentials management and detailed diagnostic log histories.", body_style)
        ],
        [
            Paragraph("Phase 8", body_style),
            Paragraph("Multilingual Localization", body_style),
            Paragraph("Implemented static and dynamic translation dictionaries for Marathi, Tamil, Telugu, Hindi, and English.", body_style)
        ],
        [
            Paragraph("Phase 9", body_style),
            Paragraph("Smart Advisories", body_style),
            Paragraph("Integrated weather-smart irrigation metrics, soil nutrient planning algorithms, and context-aware chat.", body_style)
        ],
        [
            Paragraph("Phase 10", body_style),
            Paragraph("QA & Offline Scripts", body_style),
            Paragraph("Created diagnostics tools (verify_model.py, predict.py) to validate weights compilation and local inferences.", body_style)
        ]
    ]
    
    phases_table = Table(phases_data, colWidths=[80, 160, 640])
    phases_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_light),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('TOPPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(phases_table)
    story.append(PageBreak())
    
    # ==================== SLIDE 3: PHASE 1 & 2: SETUP & DATA PREPARATION ====================
    story.append(Paragraph("Phase 1 & 2: Environment Setup & Dataset Selection", slide_title_style))
    
    p1_left = [
        Paragraph("<b>Phase 1: Environment Setup</b>", slide_subtitle_style),
        Paragraph("• <b>Libraries:</b> Installed TensorFlow and basic scientific computing packages.", bullet_style),
        Paragraph("• <b>Compatibility Diagnostics:</b> Resolved version mismatch issues between TensorFlow API boundaries, NumPy array shapes, and h5py model file serialization.", bullet_style),
        Paragraph("• <b>Outcome:</b> Established a clean, reproducible Python environment ensuring successful execution of import statements.", bullet_style),
    ]
    
    p1_right = [
        Paragraph("<b>Phase 2: Dataset Selection (PlantVillage Subset)</b>", slide_subtitle_style),
        Paragraph("• <b>Crop Scope:</b> Focused on Pepper, Potato, and Tomato crops.", bullet_style),
        Paragraph("• <b>Categories Included (15 Total):</b>", bullet_style),
        Paragraph("  - <i>Pepper:</i> Bacterial spot, Healthy", bullet_style),
        Paragraph("  - <i>Potato:</i> Early blight, Late blight, Healthy", bullet_style),
        Paragraph("  - <i>Tomato:</i> Bacterial spot, Early blight, Late blight, Leaf mold, Septoria spot, Spider mites, Target spot, Yellow leaf curl, Mosaic virus, Healthy", bullet_style),
    ]
    
    p1_table_data = [[p1_left, p1_right]]
    p1_table = Table(p1_table_data, colWidths=[430, 430])
    p1_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(p1_table)
    story.append(PageBreak())
    
    # ==================== SLIDE 4: PHASE 3: DATASET VERIFICATION ====================
    story.append(Paragraph("Phase 3: Dataset Verification & Statistics", slide_title_style))
    
    p3_left = [
        Paragraph("<b>Directory Structure Discovered & Fixed:</b>", slide_subtitle_style),
        Paragraph("• <b>Nested Folder Issue:</b> The root dataset directory path was verified and corrected to bypass a nested `PlantVillage/PlantVillage` directory, establishing the inner folder as the primary `DATASET_PATH`.", bullet_style),
        Paragraph("• <b>Loading Mechanism:</b> Configured TensorFlow's standard `image_dataset_from_directory` utility to handle label parsing.", bullet_style),
        Paragraph("• <b>Label Alignment:</b> Verified alphabetical file name loading order to prevent category index mismatches.", bullet_style),
    ]
    
    p3_right = [
        Paragraph("<b>Final Dataset Split Statistics:</b>", slide_subtitle_style),
        Paragraph("• <b>Total Loaded Images:</b> 20,638 images", bullet_style),
        Paragraph("• <b>Total Category Classes:</b> 15 classes", bullet_style),
        Paragraph("• <b>Training Subset (80% Split):</b> 16,511 images", bullet_style),
        Paragraph("• <b>Validation Subset (20% Split):</b> 4,127 images", bullet_style),
        Paragraph("• <b>Verification:</b> Verified loading and class mappings in memory to ensure stable training iterations.", bullet_style)
    ]
    
    p3_table_data = [[p3_left, p3_right]]
    p3_table = Table(p3_table_data, colWidths=[430, 430])
    p3_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(p3_table)
    story.append(PageBreak())
    
    # ==================== SLIDE 5: PHASE 4: MODEL TRAINING & ARCHITECTURE ====================
    story.append(Paragraph("Phase 4: Model Architecture & Preprocessing", slide_title_style))
    
    p4_left = [
        Paragraph("<b>Architecture Specifications:</b>", slide_subtitle_style),
        Paragraph("• <b>Base Feature Extractor:</b> Transfer learning with a pre-trained <b>MobileNetV2</b> base (weights frozen on ImageNet).", bullet_style),
        Paragraph("• <b>Regularization:</b> Configured a <b>Dropout(0.3)</b> layer before the output density head to prevent over-fitting.", bullet_style),
        Paragraph("• <b>Output Head:</b> A Dense layer with Softmax activation containing 15 classification units.", bullet_style),
        Paragraph("• <b>Data Augmentation Layers:</b> Sequentially applies Random Flip (horizontal), Random Rotation (10%), and Random Zoom (10%).", bullet_style)
    ]
    
    p4_right = [
        Paragraph("<b>Model Layer Flow Diagram:</b>", slide_subtitle_style),
        Paragraph("Input Image (RGB, 224 x 224)", code_style),
        Paragraph("  ↓<br/>Data Augmentation (Flip, Rotate, Zoom)", code_style),
        Paragraph("  ↓<br/>MobileNetV2 Preprocessing (Rescaling from [0,255] to [-1,1])", code_style),
        Paragraph("  ↓<br/>MobileNetV2 Base Backbone (Frozen weights)", code_style),
        Paragraph("  ↓<br/>GlobalAveragePooling2D", code_style),
        Paragraph("  ↓<br/>Dropout(0.3)", code_style),
        Paragraph("  ↓<br/>Dense Softmax Output (15 Classes Category probabilities)", code_style),
    ]
    
    p4_table_data = [[p4_left, p4_right]]
    p4_table = Table(p4_table_data, colWidths=[450, 410])
    p4_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(p4_table)
    story.append(PageBreak())
    
    # ==================== SLIDE 6: PHASE 5: PREDICTION SYSTEM & BUG FIX ====================
    story.append(Paragraph("Phase 5: Diagnostics & Troubleshooting Inference Bug", slide_title_style))
    
    p5_left = [
        Paragraph("<b>Bug Discovery & Anomaly:</b>", slide_subtitle_style),
        Paragraph("• <b>The Symptom:</b> During initial pipeline testing, the model predicted `Tomato_Late_blight` with ~99% confidence for nearly every uploaded image, regardless of actual crop species or leaf health.", bullet_style),
        Paragraph("• <b>Root Cause Analysis:</b> Discovered a double-preprocessing bug: `preprocess_input()` was executed twice during inference.", bullet_style),
        Paragraph("  1. Once inside the built-in preprocessing layers of the trained Keras model.", bullet_style),
        Paragraph("  2. A second time in the external input pipeline of the predictor script (`predict.py`).", bullet_style)
    ]
    
    p5_right = [
        Paragraph("<b>The Correction & Outcome:</b>", slide_subtitle_style),
        Paragraph("• <b>Resolution:</b> Removed the external `preprocess_input()` normalization step from the prediction file (`predict.py` / `app.py`).", bullet_style),
        Paragraph("• <b>Strategy:</b> Kept the input scaling sequence (`[0, 255]` to `[-1, 1]`) encapsulated strictly inside the model architecture itself.", bullet_style),
        Paragraph("• <b>Final Inference Workflow:</b>", bullet_style),
        Paragraph("<font face='Courier'>Load Image → Resize (224x224) → Convert to Array → model.predict()</font>", code_style),
        Paragraph("• <b>Outcome:</b> Model predictions aligned correctly with actual classes, restoring true validation accuracy.", bullet_style)
    ]
    
    p5_table_data = [[p5_left, p5_right]]
    p5_table = Table(p5_table_data, colWidths=[430, 430])
    p5_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(p5_table)
    story.append(PageBreak())
    
    # ==================== SLIDE 7: VALIDATION RESULTS ====================
    story.append(Paragraph("Model Evaluation & Validation Results", slide_title_style))
    
    val_left = [
        Paragraph("<b>Key Validation Performance Metrics:</b>", slide_subtitle_style),
        Paragraph("• <b>Validation Accuracy:</b> <b>89.6%</b>", bullet_style),
        Paragraph("• <b>Validation Loss:</b> <b>0.3048</b>", bullet_style),
        Paragraph("• <b>Inference Stability:</b> Verified by compiling outputs across 4,127 evaluation images.", bullet_style),
        Paragraph("• <b>Significance:</b> Confirmed that the transfer learning layers successfully generalized feature extraction (edges, color gradients, necrosis patterns) without overfitting.", bullet_style)
    ]
    
    val_right = [
        Paragraph("<b>Training Context & Performance Strategy:</b>", slide_subtitle_style),
        Paragraph("• <b>Optimizer:</b> Adam optimizer with Sparse Categorical Crossentropy loss.", bullet_style),
        Paragraph("• <b>Callback Operations:</b> EarlyStopping monitored validation loss to halt training, while ModelCheckpoint saved only the best-performing iteration to file.", bullet_style),
        Paragraph("• <b>Class Names File:</b> Exported as `class_names.txt` to guarantee translation indexes map correctly to Flask application views.", bullet_style)
    ]
    
    val_table_data = [[val_left, val_right]]
    val_table = Table(val_table_data, colWidths=[430, 430])
    val_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(val_table)
    story.append(PageBreak())
    
    # ==================== SLIDE 8: CORE FEATURES — AI DIAGNOSTICS & CHAT ====================
    story.append(Paragraph("Core Platform Features: AI Diagnostics & Support", slide_title_style))
    
    f8_left = [
        Paragraph("<b>1. Dual-Engine Diagnostics Backend</b>", slide_subtitle_style),
        Paragraph("• <b>Local Offline CNN:</b> Fast inference running on the local server for common crops (Tomato, Potato, Pepper), minimizing data costs.", bullet_style),
        Paragraph("• <b>Cloud AI Vision Fallback:</b> Uses Llama 4 Vision to identify complex pests and other crops (Apple, Wheat, Cotton, Mango, Grape, Citrus, etc.).", bullet_style),
        Paragraph("• <b>Advisory Engine:</b> Generates customized 21-day timeline guides detailing chemical/organic treatments and spray dosages.", bullet_style),
    ]
    
    f8_right = [
        Paragraph("<b>2. Multilingual AgriBot Chatbot</b>", slide_subtitle_style),
        Paragraph("• <b>Context Inheritance:</b> The chat model automatically inherits the scan context (detected disease, cause, symptoms, organic/chemical treatment) to provide customized follow-up advice.", bullet_style),
        Paragraph("• <b>Multilingual Dialog:</b> Auto-detects input and replies in the farmer's preferred language (Marathi, Tamil, Telugu, Hindi, English).", bullet_style),
        Paragraph("• <b>Accessibility:</b> Encouraging, clear, and farmer-friendly advice without overly technical jargon.", bullet_style)
    ]
    
    f8_table_data = [[f8_left, f8_right]]
    f8_table = Table(f8_table_data, colWidths=[430, 430])
    f8_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(f8_table)
    story.append(PageBreak())
    
    # ==================== SLIDE 9: CORE FEATURES — WEATHER & NUTRIENTS ====================
    story.append(Paragraph("Core Platform Features: Weather Advisory & Soil Planner", slide_title_style))
    
    f9_left = [
        Paragraph("<b>3. Weather-Smart Intelligence</b>", slide_subtitle_style),
        Paragraph("• <b>Local Climate Parsing:</b> Integrates local temp, humidity, and rain metrics to evaluate active fungal blight or pest risks.", bullet_style),
        Paragraph("• <b>Advisory Actions:</b> Prompts actions like irrigation adjustment (delaying due to rain) and foliar spray wash-away alerts.", bullet_style),
        
        Paragraph("<b>4. Growth-Stage Fertilizer Calculator</b>", slide_subtitle_style),
        Paragraph("• <b>Targeted Scheduling:</b> Custom fertilizer scheduler based on crop type, growth phase (vegetative, flowering, fruiting), and soil structure.", bullet_style),
        Paragraph("• <b>Deficiency Solutions:</b> Addresses observed leaf anomalies with organic and mineral NPK ratios.", bullet_style)
    ]
    
    f9_right = [
        Paragraph("<b>5. User Accounts & Scan Logs</b>", slide_subtitle_style),
        Paragraph("• <b>SQLite Log Base:</b> Secure registration and salted/hashed passwords (`agri_guard.db`) mapping to unique profiles.", bullet_style),
        Paragraph("• <b>History Tracking:</b> Persists details (symptoms, cause, chemical/organic treatment, photos) for farmers to review past records.", bullet_style),
        
        Paragraph("<b>6. Farmer-Friendly Localization</b>", slide_subtitle_style),
        Paragraph("• <b>Multilingual UI:</b> Static strings and dynamic recommendations map instantly to **Marathi, Tamil, Telugu, Hindi, and English**.", bullet_style)
    ]
    
    f9_table_data = [[f9_left, f9_right]]
    f9_table = Table(f9_table_data, colWidths=[430, 430])
    f9_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(f9_table)
    story.append(PageBreak())
    
    # ==================== SLIDE 10: OPERATIONAL SCRIPTS ====================
    story.append(Paragraph("Operational Pipeline & Production Deployment", slide_title_style))
    story.append(Paragraph("The verified model is integrated into a Flask web application, featuring command line maintenance scripts:", body_style))
    story.append(Spacer(1, 5))

    story.append(Paragraph("<b>1. Start the simple training pipeline (from scratch):</b>", slide_subtitle_style))
    story.append(Paragraph("<font face='Courier'>python train.py</font>", code_style))
    
    story.append(Paragraph("<b>2. Run the automated model check tool:</b>", slide_subtitle_style))
    story.append(Paragraph("<font face='Courier'>python verify_model.py</font>", code_style))
    
    story.append(Paragraph("<b>3. Execute image diagnosis predictions directly:</b>", slide_subtitle_style))
    story.append(Paragraph("<font face='Courier'>python predict.py &lt;path_to_image&gt;</font>", code_style))
    
    story.append(Paragraph("<b>4. Run the Flask Web Application locally (with SQLite logs & localized UI):</b>", slide_subtitle_style))
    story.append(Paragraph("<font face='Courier'>python app.py</font>", code_style))

    # Build Document using standard Platypus page templates
    doc.build(story, onFirstPage=draw_cover, onLaterPages=draw_slide)
    print(f"[SUCCESS] Widescreen presentation PDF generated successfully at: '{filename}'")

if __name__ == "__main__":
    make_presentation_pdf()
