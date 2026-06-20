import { useEffect, useState, useRef, useMemo } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls } from '@react-three/drei'
import * as THREE from 'three'
import './App.css'

type AppState = 'IDLE' | 'LISTENING' | 'THINKING' | 'SPEAKING'

// Vertex Shader for the particle sphere
const vertexShader = `
  uniform float uTime;
  uniform float uStateTime;
  uniform int uState; // 0=IDLE, 1=LISTENING, 2=THINKING, 3=SPEAKING
  uniform float uWaveActive;
  
  attribute float size;
  attribute float alphaOffset;
  
  varying float vAlphaOffset;
  varying vec3 vPosition;
  varying float vHighlight;
  
  // Noise functions for organic movement
  vec3 mod289(vec3 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
  vec4 mod289(vec4 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
  vec4 permute(vec4 x) { return mod289(((x*34.0)+1.0)*x); }
  vec4 taylorInvSqrt(vec4 r) { return 1.79284291400159 - 0.85373472095314 * r; }
  vec3 fade(vec3 t) { return t*t*t*(t*(t*6.0-15.0)+10.0); }
  
  float cnoise(vec3 P) {
    vec3 Pi0 = floor(P); vec3 Pi1 = Pi0 + vec3(1.0);
    Pi0 = mod289(Pi0); Pi1 = mod289(Pi1);
    vec3 Pf0 = fract(P); vec3 Pf1 = Pf0 - vec3(1.0);
    vec4 ix = vec4(Pi0.x, Pi1.x, Pi0.x, Pi1.x);
    vec4 iy = vec4(Pi0.yy, Pi1.yy);
    vec4 iz0 = Pi0.zzzz; vec4 iz1 = Pi1.zzzz;
    vec4 ixy = permute(permute(ix) + iy);
    vec4 ixy0 = permute(ixy + iz0); vec4 ixy1 = permute(ixy + iz1);
    vec4 gx0 = ixy0 * (1.0 / 7.0); vec4 gy0 = fract(floor(gx0) * (1.0 / 7.0)) - 0.5;
    gx0 = fract(gx0); vec4 gz0 = vec4(0.5) - abs(gx0) - abs(gy0);
    vec4 sz0 = step(gz0, vec4(0.0)); gx0 -= sz0 * (step(0.0, gx0) - 0.5); gy0 -= sz0 * (step(0.0, gy0) - 0.5);
    vec4 gx1 = ixy1 * (1.0 / 7.0); vec4 gy1 = fract(floor(gx1) * (1.0 / 7.0)) - 0.5;
    gx1 = fract(gx1); vec4 gz1 = vec4(0.5) - abs(gx1) - abs(gy1);
    vec4 sz1 = step(gz1, vec4(0.0)); gx1 -= sz1 * (step(0.0, gx1) - 0.5); gy1 -= sz1 * (step(0.0, gy1) - 0.5);
    vec3 g000 = vec3(gx0.x,gy0.x,gz0.x); vec3 g100 = vec3(gx0.y,gy0.y,gz0.y);
    vec3 g010 = vec3(gx0.z,gy0.z,gz0.z); vec3 g110 = vec3(gx0.w,gy0.w,gz0.w);
    vec3 g001 = vec3(gx1.x,gy1.x,gz1.x); vec3 g101 = vec3(gx1.y,gy1.y,gz1.y);
    vec3 g011 = vec3(gx1.z,gy1.z,gz1.z); vec3 g111 = vec3(gx1.w,gy1.w,gz1.w);
    vec4 norm0 = taylorInvSqrt(vec4(dot(g000, g000), dot(g010, g010), dot(g100, g100), dot(g110, g110)));
    g000 *= norm0.x; g010 *= norm0.y; g100 *= norm0.z; g110 *= norm0.w;
    vec4 norm1 = taylorInvSqrt(vec4(dot(g001, g001), dot(g011, g011), dot(g101, g101), dot(g111, g111)));
    g001 *= norm1.x; g011 *= norm1.y; g101 *= norm1.z; g111 *= norm1.w;
    float n000 = dot(g000, Pf0); float n100 = dot(g100, vec3(Pf1.x, Pf0.yz));
    float n010 = dot(g010, vec3(Pf0.x, Pf1.y, Pf0.z)); float n110 = dot(g110, vec3(Pf1.xy, Pf0.z));
    float n001 = dot(g001, vec3(Pf0.xy, Pf1.z)); float n101 = dot(g101, vec3(Pf1.x, Pf0.y, Pf1.z));
    float n011 = dot(g011, vec3(Pf0.x, Pf1.yz)); float n111 = dot(g111, Pf1);
    vec3 fade_xyz = fade(Pf0);
    vec4 n_z = mix(vec4(n000, n100, n010, n110), vec4(n001, n101, n011, n111), fade_xyz.z);
    vec2 n_yz = mix(n_z.xy, n_z.zw, fade_xyz.y);
    float n_xyz = mix(n_yz.x, n_yz.y, fade_xyz.x); 
    return 2.2 * n_xyz;
  }

  void main() {
    vAlphaOffset = alphaOffset;
    
    // Base position
    vec3 pos = position;
    vPosition = pos;
    
    // Calculate noise based on time and state
    float noiseFreq = 1.5;
    float noiseAmp = 0.05;
    float timeSpeed = 0.2;
    
    if (uState == 1) { // LISTENING
      noiseAmp = 0.02;
      timeSpeed = 0.1;
    } else if (uState == 2) { // THINKING
      noiseFreq = 2.5;
      noiseAmp = 0.15;
      timeSpeed = 1.2;
    } else if (uState == 3) { // SPEAKING
      noiseFreq = 2.0;
      noiseAmp = mix(0.1, 0.2, (sin(uStateTime * 15.0) + 1.0) * 0.5); // Pulse to voice
      timeSpeed = 1.5;
    }
    
    // Apply noise displacement along normals (sphere expansion/contraction)
    vec3 norm = normalize(pos);
    float noise = cnoise(norm * noiseFreq + uTime * timeSpeed);
    pos += norm * noise * noiseAmp;
    
    // "Radar Wave" sweeping effect (for LISTENING/SPEAKING/THINKING)
    vHighlight = 0.0;
    if (uState > 0) {
      // Create a sweeping band based on the Y position and time
      float waveFreq = 1.0;
      float waveSpeed = uState == 2 ? 3.0 : 1.5; 
      
      // Calculate distance to the "wave front"
      float wavePos = sin(pos.y * waveFreq - uTime * waveSpeed);
      // Create a sharp band
      vHighlight = smoothstep(0.8, 1.0, wavePos);
      
      // Expand particles slightly at the wave front
      pos += norm * vHighlight * 0.1;
    }

    vec4 mvPosition = modelViewMatrix * vec4(pos, 1.0);
    
    // Size attenuation based on depth and state
    float pointSize = size;
    if (uState == 3) pointSize *= 1.2 + vHighlight * 0.5; // Bigger when speaking
    if (uState == 2) pointSize *= 1.0 + vHighlight * 0.8; // High contrast when thinking
    
    gl_PointSize = pointSize * (20.0 / -mvPosition.z);
    gl_Position = projectionMatrix * mvPosition;
  }
`

// Fragment Shader
const fragmentShader = `
  uniform float uTime;
  uniform int uState;
  
  varying float vAlphaOffset;
  varying vec3 vPosition;
  varying float vHighlight;

  void main() {
    // Make particles circular
    vec2 cxy = 2.0 * gl_PointCoord - 1.0;
    float r = dot(cxy, cxy);
    if (r > 1.0) discard;
    
    // Soft edge alpha
    float alpha = 1.0 - smoothstep(0.8, 1.0, sqrt(r));
    
    // Base opacity pulse
    float baseOpacity = 0.4 + 0.3 * sin(uTime * 2.0 + vAlphaOffset);
    
    // Colors
    vec3 colorIdle = vec3(0.0, 0.7, 1.0);     // Cyan
    vec3 colorListen = vec3(0.0, 0.9, 1.0);   // Bright Cyan
    vec3 colorThink = vec3(0.6, 0.2, 1.0);    // Purple/Violet
    vec3 colorSpeak = vec3(0.0, 1.0, 0.8);    // Cyan/Green iridescent
    
    vec3 color = colorIdle;
    float finalOpacity = baseOpacity;
    
    if (uState == 1) { // LISTENING
      color = mix(colorIdle, colorListen, 0.8);
      // Bright wave sweeps across
      color = mix(color, vec3(1.0, 1.0, 1.0), vHighlight * 0.8);
      finalOpacity = mix(0.5, 1.0, vHighlight);
    } 
    else if (uState == 2) { // THINKING
      // Mix purple with cyan based on position for a neat aurora effect
      float mixVal = (sin(vPosition.x * 2.0 + uTime) + 1.0) * 0.5;
      color = mix(colorThink, colorListen, mixVal);
      // Very bright fast wave
      color = mix(color, vec3(1.0, 0.8, 1.0), vHighlight * 0.9);
      finalOpacity = mix(0.6, 1.0, vHighlight);
    } 
    else if (uState == 3) { // SPEAKING
      // Iridescent mix
      float mixY = (sin(vPosition.y * 3.0 - uTime * 2.0) + 1.0) * 0.5;
      float mixZ = (cos(vPosition.z * 3.0 + uTime * 2.0) + 1.0) * 0.5;
      color = mix(colorSpeak, colorThink, mixY * mixZ);
      // Pulsing brightness
      color = mix(color, vec3(0.8, 1.0, 0.9), vHighlight * 0.7);
      finalOpacity = mix(0.7, 1.0, vHighlight);
    }

    gl_FragColor = vec4(color, alpha * finalOpacity);
  }
`

// The 3D Sphere Component
function ParticleSphere({ state }: { state: AppState }) {
  const pointsRef = useRef<THREE.Points>(null)
  const materialRef = useRef<THREE.ShaderMaterial>(null)
  
  // State tracking for shader uniforms
  const stateEnum = state === 'IDLE' ? 0 : state === 'LISTENING' ? 1 : state === 'THINKING' ? 2 : 3
  const [stateTime, setStateTime] = useState(0)
  const lastStateRef = useRef(state)

  // Generate particle geometry
  const [positions, sizes, alphas] = useMemo(() => {
    const count = 3000; // High fidelity
    const pos = new Float32Array(count * 3)
    const sz = new Float32Array(count)
    const alph = new Float32Array(count)
    
    // Fibonacci sphere distribution for even spread
    const goldenRatio = (1 + Math.sqrt(5)) / 2
    
    for (let i = 0; i < count; i++) {
      // Distribute points on a sphere radius 2.0
      const theta = 2 * Math.PI * i / goldenRatio
      const phi = Math.acos(1 - 2 * (i + 0.5) / count)
      
      const r = 2.0
      pos[i * 3] = r * Math.sin(phi) * Math.cos(theta)
      pos[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta)
      pos[i * 3 + 2] = r * Math.cos(phi)
      
      // Randomize sizes and alpha phases
      sz[i] = Math.random() * 2.5 + 1.0
      alph[i] = Math.random() * Math.PI * 2
    }
    
    return [pos, sz, alph]
  }, [])

  // Animation Loop
  useFrame((clockState) => {
    const time = clockState.clock.elapsedTime
    
    if (state !== lastStateRef.current) {
      setStateTime(time) // Reset state timer on transition
      lastStateRef.current = state
    }

    if (materialRef.current) {
      materialRef.current.uniforms.uTime.value = time
      materialRef.current.uniforms.uStateTime.value = time - stateTime
      
      // Smoothly transition state enum to avoid popping (though integer in shader, we pass raw)
      // Actually, passing as int is fine since we handle smooth transitions in the shader math
      materialRef.current.uniforms.uState.value = stateEnum
    }
    
    // Slow base rotation
    if (pointsRef.current) {
      pointsRef.current.rotation.y = time * 0.1
      pointsRef.current.rotation.x = Math.sin(time * 0.05) * 0.2
    }
  })

  return (
    <points ref={pointsRef}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" count={positions.length / 3} array={positions} itemSize={3} />
        <bufferAttribute attach="attributes-size" count={sizes.length} array={sizes} itemSize={1} />
        <bufferAttribute attach="attributes-alphaOffset" count={alphas.length} array={alphas} itemSize={1} />
      </bufferGeometry>
      <shaderMaterial
        ref={materialRef}
        vertexShader={vertexShader}
        fragmentShader={fragmentShader}
        uniforms={{
          uTime: { value: 0 },
          uStateTime: { value: 0 },
          uState: { value: 0 },
        }}
        transparent={true}
        depthWrite={false}
        blending={THREE.AdditiveBlending}
      />
    </points>
  )
}

export default function App() {
  const [state, setState] = useState<AppState>('IDLE')

  useEffect(() => {
    let ws: WebSocket
    const connect = () => {
      ws = new WebSocket('ws://127.0.0.1:8765/ws')
      ws.onopen = () => console.log('Julie connected')
      ws.onmessage = (e) => {
        try {
          const msg = JSON.parse(e.data)
          if (msg.type === 'STATE_CHANGE') setState(msg.payload.state as AppState)
        } catch {}
      }
      ws.onclose = () => setTimeout(connect, 3000)
    }
    connect()
    return () => ws?.close()
  }, [])

  // Glow color based on state
  const glowColors = {
    IDLE: 'rgba(0, 150, 200, 0.1)',
    LISTENING: 'rgba(0, 240, 255, 0.3)',
    THINKING: 'rgba(140, 100, 255, 0.3)',
    SPEAKING: 'rgba(0, 255, 200, 0.4)',
  }

  return (
    <div className="orb-root">
      <div className="orb-container">
        <Canvas 
          camera={{ position: [0, 0, 5], fov: 45 }}
          gl={{ alpha: true, antialias: true }}
        >
          <ParticleSphere state={state} />
        </Canvas>
      </div>
    </div>
  )
}
