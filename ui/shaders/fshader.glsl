#ifdef GL_ES
// Set default precision to medium
precision mediump int;
precision mediump float;
#endif

varying vec4 v_col;

void main()
{
    gl_FragColor = v_col;
}