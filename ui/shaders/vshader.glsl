#ifdef GL_ES
    precision highp float;
#endif

attribute vec3 position;
attribute vec3 normal;

attribute lowp vec3 colour;
attribute vec2 texcoord;

uniform mat4 mv_matrix;
uniform mat4 p_matrix;
uniform mat4 norm_matrix;

struct lightSource
{
  vec4 position;
  vec4 diffuse;
};

lightSource frontLight = lightSource(
    vec4(0.0, 0.0, -100.0, 0.0),
    vec4(1.0, 0.7, 1.0, 1.0)
);
lightSource backLight = lightSource(
    vec4(10.0, 0.0, 100.0, 0.0),
    vec4(0.7, 1.0, 1.0, 1.0)
);


varying lowp vec4 v_col;

vec3 diffuseReflection(lightSource light, in vec3 normal) {
    // Calculate the diffuse reflection of the given light source for the normal.
    vec4 normalDir = normalize(norm_matrix * vec4(normal,0.0));
    vec4 lightDirection = normalize(norm_matrix * light.position);
    return vec3(light.diffuse) * vec3(colour)
      * max(0.0, dot(normalDir, lightDirection));
}

void main (void) {
    vec4 pos = mv_matrix * vec4(position,1.0);
    
    v_col = vec4(diffuseReflection(frontLight, normal), 1.0)
           + vec4(diffuseReflection(backLight, normal), 1.0)
           + vec4(colour * 0.3, 0.7);

    gl_Position = p_matrix * pos;
}
