import 'dart:async';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:dio/dio.dart';
import 'dart:io';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:record/record.dart';
import 'package:audioplayers/audioplayers.dart';
import 'package:path_provider/path_provider.dart';
import '../../../core/network/api_client.dart';
import '../../../core/network/socket_service.dart';
import '../../../core/storage/local_storage.dart';
import '../../../core/theme/app_colors.dart';
import '../../../shared/components/typography/t_text.dart';
import '../../../shared/components/loaders/t_loader.dart';
import '../models/chat_message.dart';

const _micSvg = '''<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" y1="19" x2="12" y2="22"/></svg>''';
const _sendSvg = '''<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>''';
const _photoSvg = '''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"></path><circle cx="12" cy="13" r="4"></circle></svg>''';


class ChatView extends StatefulWidget {
  final int emergenciaId;
  final bool showAppBar;

  const ChatView({super.key, required this.emergenciaId, this.showAppBar = true});

  @override
  State<ChatView> createState() => _ChatViewState();
}

class _ChatViewState extends State<ChatView> {
  final TextEditingController _messageController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  final List<ChatMessage> _messages = [];
  bool _isLoading = true;
  bool _isFinished = false;
  bool _isRecording = false;
  bool _isTyping = false;
  String? _userRole;
  late final AudioRecorder _audioRecorder;
  String? _audioPath;

  StreamSubscription? _socketSubscription;

  @override
  void initState() {
    super.initState();
    _audioRecorder = AudioRecorder();
    _messageController.addListener(() {
      setState(() {
        _isTyping = _messageController.text.trim().isNotEmpty;
      });
    });
    _loadInitialData();
  }

  Future<void> _loadInitialData() async {
    try {
      final storage = LocalStorage();
      final apiClient = ApiClient(localStorage: storage);
      
      final role = await storage.getRol();

      // Obtener mensajes y estado de la emergencia
      final responses = await Future.wait([
        apiClient.dio.get('/chat/${widget.emergenciaId}'),
        apiClient.dio.get('/emergencias/${widget.emergenciaId}'), // Necesitamos este endpoint
      ]);
      
      final List<dynamic> messagesData = responses[0].data;
      final emergencyData = responses[1].data;
      
      final status = emergencyData['estado']?['nombre'] ?? '';
      _isFinished = (status == 'COMPLETADA' || status == 'CANCELADA');

      if (mounted) {
        setState(() {
          _userRole = role;
          _messages.addAll(messagesData.map((m) => ChatMessage.fromJson(m)).toList());
          _isLoading = false;
        });
        
        if (!_isFinished) {
          _initSocket();
        }
        
        _scrollToBottom();
      }
    } catch (e) {
      debugPrint('Error loading chat or emergency: $e');
      if (mounted) setState(() => _isLoading = false);
    }
  }

  void _initSocket() {
    // Solo conectar si el socket no está activo
    SocketService().connect();
    
    _socketSubscription = SocketService().stream.listen((message) {
      if (message['type'] == 'chat_message' && 
          message['idEmergencia'].toString() == widget.emergenciaId.toString()) {
        if (mounted) {
          setState(() {
            final newMessage = ChatMessage.fromJson(message);
            // Evitar duplicados si el mensaje ya fue añadido por el método _sendMessage
            if (!_messages.any((m) => m.id == newMessage.id)) {
              _messages.add(newMessage);
              _scrollToBottom();
            }
          });
        }
      }
    });
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  Future<void> _sendMessage({String? text, String? imageUrl}) async {
    if (text == null && imageUrl == null) return;

    final storage = LocalStorage();
    final apiClient = ApiClient(localStorage: storage);

    try {
      final response = await apiClient.dio.post(
        '/chat/${widget.emergenciaId}',
        data: {
          'contenido': text,
          'imagen_url': imageUrl,
        },
      );

      if (mounted) {
        final newMessage = ChatMessage.fromJson(response.data);
        setState(() {
          // Si el socket ya lo añadió, no duplicar (aunque el socket suele ser para el otro extremo)
          if (!_messages.any((m) => m.id == newMessage.id)) {
            _messages.add(newMessage);
          }
        });
        _scrollToBottom();
      }
    } catch (e) {
      debugPrint('Error sending message: $e');
    }
  }

  Future<void> _pickAndUploadImage() async {
    final picker = ImagePicker();
    final image = await picker.pickImage(source: ImageSource.gallery);
    if (image == null) return;
    
    await _uploadMediaFile(File(image.path));
  }

  Future<void> _uploadMediaFile(File file) async {
    try {
      final storage = LocalStorage();
      final apiClient = ApiClient(localStorage: storage);
      
      final fileName = file.path.split('/').last;
      final formData = FormData.fromMap({
        'file': await MultipartFile.fromFile(file.path, filename: fileName),
      });

      final response = await apiClient.dio.post(
        '/chat/${widget.emergenciaId}/upload_media',
        data: formData,
      );

      if (mounted) {
        final newMessage = ChatMessage.fromJson(response.data);
        setState(() {
          _messages.add(newMessage);
        });
        _scrollToBottom();
      }
    } catch (e) {
      debugPrint('Error uploading media: $e');
    }
  }

  Future<void> _startRecording() async {
    if (_isRecording) return;
    try {
      if (await _audioRecorder.hasPermission()) {
        final dir = await getTemporaryDirectory();
        _audioPath = '${dir.path}/audio_${DateTime.now().millisecondsSinceEpoch}.m4a';
        await _audioRecorder.start(const RecordConfig(), path: _audioPath!);
        setState(() => _isRecording = true);
      }
    } catch (e) {
      debugPrint('Error starting record: $e');
    }
  }

  Future<void> _stopRecordingAndSend() async {
    if (!_isRecording) return;
    try {
      final path = await _audioRecorder.stop();
      setState(() => _isRecording = false);
      if (path != null) {
        _uploadMediaFile(File(path));
      }
    } catch (e) {
      debugPrint('Error stopping record: $e');
    }
  }

  void _cancelRecording() async {
    await _audioRecorder.stop();
    setState(() => _isRecording = false);
  }

  @override
  void dispose() {
    _socketSubscription?.cancel();
    SocketService().disconnect(); // Cerrar socket al salir del chat
    _messageController.dispose();
    _scrollController.dispose();
    _audioRecorder.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: widget.showAppBar ? AppBar(
        title: TText.h3('Chat de Auxilio'),
      ) : null,
      body: Column(
        children: [
          Expanded(
            child: _isLoading 
              ? const Center(child: TLoader())
              : ListView.builder(
                  controller: _scrollController,
                  padding: const EdgeInsets.all(16),
                  itemCount: _messages.length,
                  itemBuilder: (context, index) {
                    final msg = _messages[index];
                    final isMe = msg.rolRemitente == (_userRole ?? 'cliente');
                    return _ChatBubble(message: msg, isMe: isMe);
                  },
                ),
          ),
          if (!_isFinished) 
            _buildInputArea()
          else
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(16),
              color: AppColors.neutral200,
              child: TText.body(
                'Esta emergencia ha finalizado. El chat es de solo lectura.',
                textAlign: TextAlign.center,
                color: AppColors.textMuted,
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildInputArea() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 12),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.1),
            blurRadius: 4,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: SafeArea(
        child: Row(
          children: [
            IconButton(
              icon: SvgPicture.string(_photoSvg, colorFilter: const ColorFilter.mode(AppColors.primary, BlendMode.srcIn)),
              onPressed: _pickAndUploadImage,
            ),
            Expanded(
              child: TextField(
                controller: _messageController,
                decoration: InputDecoration(
                  hintText: _isRecording ? 'Grabando audio...' : 'Escribe un mensaje...',
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.zero,
                    borderSide: BorderSide.none,
                  ),
                  filled: true,
                  fillColor: _isRecording ? Colors.red.withValues(alpha: 0.1) : AppColors.neutral100,
                  contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                ),
                maxLines: null,
                readOnly: _isRecording,
              ),
            ),
            const SizedBox(width: 8),
            GestureDetector(
              onLongPressStart: _isTyping ? null : (_) {
                if (!_isRecording) _startRecording();
              },
              onLongPressEnd: _isTyping ? null : (_) {
                if (_isRecording) _stopRecordingAndSend();
              },
              onLongPressUp: _isTyping ? null : () {},
              onLongPressCancel: _isTyping ? null : _cancelRecording,
              onTap: _isTyping ? () {
                final text = _messageController.text.trim();
                if (text.isNotEmpty) {
                  _sendMessage(text: text);
                  _messageController.clear();
                }
              } : () {
                if (_isRecording) {
                  _stopRecordingAndSend();
                } else {
                  _startRecording();
                }
              },
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 200),
                padding: EdgeInsets.all(_isRecording ? 16 : 12),
                decoration: BoxDecoration(
                  color: _isRecording ? Colors.red : AppColors.primary,
                  shape: BoxShape.rectangle,
                ),
                child: SvgPicture.string(_isTyping ? _sendSvg : _micSvg),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _ChatBubble extends StatefulWidget {
  final ChatMessage message;
  final bool isMe;

  const _ChatBubble({required this.message, required this.isMe});

  @override
  State<_ChatBubble> createState() => _ChatBubbleState();
}

class _ChatBubbleState extends State<_ChatBubble> {
  final AudioPlayer _audioPlayer = AudioPlayer();
  bool _isPlaying = false;
  Duration _duration = Duration.zero;
  Duration _position = Duration.zero;

  @override
  void initState() {
    super.initState();
    if (widget.message.audioUrl != null) {
      _audioPlayer.onPlayerStateChanged.listen((state) {
        if (mounted) setState(() => _isPlaying = state == PlayerState.playing);
      });
      _audioPlayer.onDurationChanged.listen((d) {
        if (mounted) setState(() => _duration = d);
      });
      _audioPlayer.onPositionChanged.listen((p) {
        if (mounted) setState(() => _position = p);
      });
    }
  }

  @override
  void dispose() {
    _audioPlayer.dispose();
    super.dispose();
  }

  void _playPauseAudio() async {
    if (_isPlaying) {
      await _audioPlayer.pause();
    } else {
      await _audioPlayer.play(UrlSource('${ApiClient.serverUrl}/${widget.message.audioUrl}'));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: widget.isMe ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.75),
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: widget.isMe ? AppColors.primary : AppColors.neutral200,
          borderRadius: BorderRadius.zero,
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (widget.message.imagenUrl != null) ...[
              GestureDetector(
                onTap: () {
                  showDialog(
                    context: context,
                    builder: (context) => Dialog(
                      backgroundColor: Colors.transparent,
                      insetPadding: EdgeInsets.zero,
                      child: Stack(
                        fit: StackFit.expand,
                        children: [
                          InteractiveViewer(
                            panEnabled: true,
                            minScale: 0.5,
                            maxScale: 4,
                            child: Image.network(
                              '${ApiClient.serverUrl}/${widget.message.imagenUrl}',
                              fit: BoxFit.contain,
                            ),
                          ),
                          Positioned(
                            top: 40,
                            right: 20,
                            child: IconButton(
                              icon: const Icon(Icons.close, color: Colors.white, size: 30),
                              onPressed: () => Navigator.of(context).pop(),
                            ),
                          ),
                        ],
                      ),
                    ),
                  );
                },
                child: ClipRRect(
                  borderRadius: BorderRadius.zero,
                  child: Image.network(
                    '${ApiClient.serverUrl}/${widget.message.imagenUrl}',
                    errorBuilder: (context, error, stackTrace) => const Icon(Icons.broken_image),
                  ),
                ),
              ),
              if (widget.message.contenido != null || widget.message.audioUrl != null) const SizedBox(height: 8),
            ],
            
            if (widget.message.audioUrl != null) ...[
              Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  GestureDetector(
                    onTap: _playPauseAudio,
                    child: Icon(
                      _isPlaying ? Icons.pause_circle_filled : Icons.play_circle_fill,
                      color: widget.isMe ? Colors.white : Colors.black87,
                      size: 36,
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: SliderTheme(
                      data: SliderThemeData(
                        thumbShape: const RoundSliderThumbShape(enabledThumbRadius: 6),
                        trackHeight: 2,
                        activeTrackColor: widget.isMe ? Colors.white : AppColors.primary,
                        inactiveTrackColor: widget.isMe ? Colors.white38 : Colors.black12,
                        thumbColor: widget.isMe ? Colors.white : AppColors.primary,
                      ),
                      child: Slider(
                        value: _position.inMilliseconds.toDouble(),
                        min: 0,
                        max: _duration.inMilliseconds > 0 ? _duration.inMilliseconds.toDouble() : 1,
                        onChanged: (value) {
                          _audioPlayer.seek(Duration(milliseconds: value.toInt()));
                        },
                      ),
                    ),
                  ),
                ],
              ),
              if (widget.message.contenido != null) const SizedBox(height: 8),
            ],

            if (widget.message.contenido != null && widget.message.contenido!.isNotEmpty)
              Text(
                widget.message.contenido!,
                style: TextStyle(
                  color: widget.isMe ? Colors.white : Colors.black87,
                ),
              ),
          ],
        ),
      ),
    );
  }
}
