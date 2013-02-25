gst-launch multifilesrc index=0 location="/tmp/%06d.png" caps="image/png,framerate=1/1" ! pngdec ! ffmpegcolorspace ! tee name=t_vid ! queue ! ffmpegcolorspace !  video/x-raw-yuv,framerate=1/1 ! xvimagesink
#sdlvideosink  #sync=false t_vid. ! queue ! pngenc snapshot=0 ! multifilesink location="./tests/osequence/%04d.png" index=1
