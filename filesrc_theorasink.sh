gst-launch -vvv multifilesrc index=0 location="/tmp/%06d.png" caps="image/png,framerate=1/1" ! pngdec ! ffmpegcolorspace ! videorate max-rate=25 force-fps=25/1 ! theoraenc ! oggmux ! filesink location=out.ogg
#sdlvideosink  #sync=false t_vid. ! queue ! pngenc snapshot=0 ! multifilesink location="./tests/osequence/%04d.png" index=1
