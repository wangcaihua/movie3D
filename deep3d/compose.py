from absl import flags, app
from moviepy.editor import *

FLAGS = flags.FLAGS

flags.DEFINE_string('ia', None, 'audio_in')
flags.DEFINE_string('iv', None, 'video_in')
flags.DEFINE_string('ov', None, 'video_out')
flags.DEFINE_string('codec', 'mpeg4', 'codec')
flags.DEFINE_string('bitrate', '2000k', 'bitrate')


def compose(audio_in: str, video_in: str, video_out: str,
            codec: str = 'mpeg4', bitrate='2000k'):
  audio_in_clip = AudioFileClip(audio_in)
  video_in_clip = VideoFileClip(video_in)
  video_out_clip = video_in_clip.set_audio(audio_in_clip)
  video = CompositeVideoClip([video_out_clip])
  video.write_videofile(video_out, codec=codec, bitrate=bitrate)


def main(_):
  compose(FLAGS.ia, FLAGS.iv, FLAGS.ov,
          codec=FLAGS.codec,
          bitrate=FLAGS.bitrate)


if __name__ == '__main__':
  app.run(main)
