import React, { useState, useRef, useEffect } from 'react';
import {
  Play,
  Pause,
  RotateCcw,
  Volume2,
  VolumeX,
  Download,
  Gauge,
  Sparkles,
} from 'lucide-react';
import Button from '../common/Button';

export const AudioPlayer = ({
  audioUrl,
  textToNarrate = '',
  title = 'Spoken Narration',
  className = '',
}) => {
  const audioRef = useRef(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [playbackRate, setPlaybackRate] = useState(1.0);
  const [isMuted, setIsMuted] = useState(false);
  const [announcement, setAnnouncement] = useState('');

  const speeds = [0.75, 1.0, 1.25, 1.5, 2.0];

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const updateTime = () => setCurrentTime(audio.currentTime);
    const updateDuration = () => setDuration(audio.duration || 0);
    const handleEnded = () => {
      setIsPlaying(false);
      setCurrentTime(0);
      setAnnouncement('Audio playback finished.');
    };

    audio.addEventListener('timeupdate', updateTime);
    audio.addEventListener('loadedmetadata', updateDuration);
    audio.addEventListener('ended', handleEnded);

    return () => {
      audio.removeEventListener('timeupdate', updateTime);
      audio.removeEventListener('loadedmetadata', updateDuration);
      audio.removeEventListener('ended', handleEnded);
    };
  }, [audioUrl]);

  const togglePlay = () => {
    if (audioUrl && audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
        setIsPlaying(false);
        setAnnouncement('Audio paused');
      } else {
        audioRef.current.play().catch((e) => console.error('Play error:', e));
        setIsPlaying(true);
        setAnnouncement('Audio playing');
      }
    } else if (textToNarrate && typeof window !== 'undefined' && 'speechSynthesis' in window) {
      if (isPlaying) {
        window.speechSynthesis.cancel();
        setIsPlaying(false);
        setAnnouncement('Speech narration paused');
      } else {
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(textToNarrate);
        utterance.rate = playbackRate;
        utterance.onend = () => {
          setIsPlaying(false);
          setAnnouncement('Speech narration completed');
        };
        utterance.onerror = () => setIsPlaying(false);
        window.speechSynthesis.speak(utterance);
        setIsPlaying(true);
        setAnnouncement('Browser speech narration playing');
      }
    }
  };

  const handleReplay = () => {
    if (audioUrl && audioRef.current) {
      audioRef.current.currentTime = 0;
      audioRef.current.play();
      setIsPlaying(true);
      setAnnouncement('Audio restarted from beginning');
    } else if (textToNarrate && typeof window !== 'undefined' && 'speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      togglePlay();
    }
  };

  const handleSeek = (e) => {
    if (!audioRef.current) return;
    const newTime = parseFloat(e.target.value);
    audioRef.current.currentTime = newTime;
    setCurrentTime(newTime);
  };

  const handleSpeedChange = (rate) => {
    if (!audioRef.current) return;
    audioRef.current.playbackRate = rate;
    setPlaybackRate(rate);
    setAnnouncement(`Playback speed set to ${rate}x`);
  };

  const toggleMute = () => {
    if (!audioRef.current) return;
    audioRef.current.muted = !isMuted;
    setIsMuted(!isMuted);
    setAnnouncement(isMuted ? 'Audio unmuted' : 'Audio muted');
  };

  const formatTime = (secs) => {
    if (isNaN(secs)) return '0:00';
    const m = Math.floor(secs / 60);
    const s = Math.floor(secs % 60);
    return `${m}:${s < 10 ? '0' : ''}${s}`;
  };

  return (
    <div
      role="region"
      aria-label="Accessible Audio Narration Player"
      className={`bg-indigo-900 text-white rounded-2xl p-6 shadow-lg space-y-4 ${className}`}
      onKeyDown={(e) => {
        if (e.key === ' ' && e.target.tagName !== 'INPUT' && e.target.tagName !== 'BUTTON') {
          e.preventDefault();
          togglePlay();
        }
      }}
    >
      {/* Screen Reader Live Announcement */}
      <div className="sr-only" aria-live="assertive">
        {announcement}
      </div>

      <audio ref={audioRef} src={audioUrl} preload="metadata" />

      {/* Header */}
      <div className="flex items-center justify-between pb-2 border-b border-indigo-800/80">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-lg bg-indigo-800 text-indigo-300">
            <Volume2 className="w-5 h-5" aria-hidden="true" />
          </div>
          <div>
            <h4 className="font-semibold text-white text-base">{title}</h4>
            <p className="text-xs text-indigo-300">Piper Neural Voice Narration</p>
          </div>
        </div>

        {audioUrl && (
          <a
            href={audioUrl}
            download="narration.wav"
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-800/60 hover:bg-indigo-800 text-indigo-200 hover:text-white text-xs font-medium transition-colors focus:ring-2 focus:ring-indigo-400 focus:outline-none"
            aria-label="Download audio narration file"
          >
            <Download className="w-4 h-4" aria-hidden="true" />
            <span className="hidden sm:inline">Download Audio</span>
          </a>
        )}
      </div>

      {/* Progress & Time */}
      <div className="space-y-1.5">
        <div className="flex items-center justify-between text-xs font-mono text-indigo-300">
          <span>{formatTime(currentTime)}</span>
          <span>{formatTime(duration)}</span>
        </div>
        <input
          type="range"
          min="0"
          max={duration || 100}
          value={currentTime}
          onChange={handleSeek}
          aria-label="Audio playback seek bar"
          className="w-full h-2 bg-indigo-800 rounded-lg appearance-none cursor-pointer accent-indigo-400 focus:outline-none focus:ring-2 focus:ring-indigo-300"
        />
      </div>

      {/* Primary Controls */}
      <div className="flex flex-wrap items-center justify-between gap-4 pt-2">
        <div className="flex items-center gap-2">
          <button
            onClick={togglePlay}
            aria-label={isPlaying ? 'Pause audio narration' : 'Play audio narration'}
            className="w-12 h-12 rounded-xl bg-white hover:bg-slate-100 text-indigo-900 flex items-center justify-center font-bold shadow-md transition-all focus:outline-none focus:ring-4 focus:ring-indigo-400 cursor-pointer"
          >
            {isPlaying ? (
              <Pause className="w-6 h-6 fill-current" aria-hidden="true" />
            ) : (
              <Play className="w-6 h-6 fill-current translate-x-0.5" aria-hidden="true" />
            )}
          </button>

          <button
            onClick={handleReplay}
            aria-label="Replay audio narration from beginning"
            className="p-3 rounded-xl bg-indigo-800 hover:bg-indigo-700 text-white transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-400 cursor-pointer"
          >
            <RotateCcw className="w-5 h-5" aria-hidden="true" />
          </button>

          <button
            onClick={toggleMute}
            aria-label={isMuted ? 'Unmute audio' : 'Mute audio'}
            className="p-3 rounded-xl bg-indigo-800 hover:bg-indigo-700 text-white transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-400 cursor-pointer"
          >
            {isMuted ? (
              <VolumeX className="w-5 h-5" aria-hidden="true" />
            ) : (
              <Volume2 className="w-5 h-5" aria-hidden="true" />
            )}
          </button>
        </div>

        {/* Speed Selector */}
        <div className="flex items-center gap-1.5" role="group" aria-label="Playback speed selector">
          <Gauge className="w-4 h-4 text-indigo-300 mr-1" aria-hidden="true" />
          {speeds.map((rate) => (
            <button
              key={rate}
              onClick={() => handleSpeedChange(rate)}
              className={`px-2.5 py-1 rounded-lg text-xs font-semibold transition-all focus:outline-none focus:ring-2 focus:ring-indigo-400 cursor-pointer ${
                playbackRate === rate
                  ? 'bg-indigo-500 text-white shadow-sm'
                  : 'bg-indigo-800/80 hover:bg-indigo-700 text-indigo-200'
              }`}
              aria-pressed={playbackRate === rate}
              aria-label={`Set speed to ${rate}x`}
            >
              {rate}x
            </button>
          ))}
        </div>
      </div>

      {/* Corresponding text reading display */}
      {textToNarrate && (
        <div className="mt-4 p-4 rounded-xl bg-indigo-950/60 border border-indigo-800/60 text-indigo-100 text-sm leading-relaxed max-h-36 overflow-y-auto">
          <div className="text-xs font-semibold text-indigo-400 uppercase tracking-wider mb-1">
            Narration Transcript:
          </div>
          <p>{textToNarrate}</p>
        </div>
      )}
    </div>
  );
};
export default AudioPlayer;

