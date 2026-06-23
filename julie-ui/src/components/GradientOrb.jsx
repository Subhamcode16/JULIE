import React, { useRef, useMemo, useState } from 'react';
import { useFrame, extend } from '@react-three/fiber';
import { shaderMaterial, OrbitControls, Environment } from '@react-three/drei';
import { EffectComposer, Bloom } from '@react-three/postprocessing';
import * as THREE from 'three';

// --------------------------------------------------------
// SHADER MATERIALS
// --------------------------------------------------------

const OrbMaterial = shaderMaterial(
  {
    uColorA: new THREE.Color("#ff4fd8"),
    uColorB: new THREE.Color("#5b8cff"),
    uColorC: new THREE.Color("#b06bff"),
    uNoiseOffset: new THREE.Vector3(0, 0, 0),
    uFresnelIntensity: 0.7,
    uSpecularIntensity: 0.8,
  },
  // Vertex Shader
  `
    varying vec2 vUv;
    varying vec3 vNormal;
    varying vec3 vViewPosition;
    varying vec3 vWorldPosition;

    void main() {
      vUv = uv;
      vNormal = normalize(normalMatrix * normal);
      
      vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
      vViewPosition = -mvPosition.xyz;
      
      vec4 worldPosition = modelMatrix * vec4(position, 1.0);
      vWorldPosition = worldPosition.xyz;
      
      gl_Position = projectionMatrix * mvPosition;
    }
  `,
  // Fragment Shader
  `
    uniform vec3 uColorA;
    uniform vec3 uColorB;
    uniform vec3 uColorC;
    uniform vec3 uNoiseOffset;
    uniform float uFresnelIntensity;
    uniform float uSpecularIntensity;

    varying vec2 vUv;
    varying vec3 vNormal;
    varying vec3 vViewPosition;
    varying vec3 vWorldPosition;

    // --- Simplex 3D Noise ---
    vec3 mod289(vec3 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
    vec4 mod289(vec4 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
    vec4 permute(vec4 x) { return mod289(((x*34.0)+1.0)*x); }
    vec4 taylorInvSqrt(vec4 r) { return 1.79284291400159 - 0.85373472095314 * r; }

    float snoise(vec3 v) {
      const vec2  C = vec2(1.0/6.0, 1.0/3.0);
      const vec4  D = vec4(0.0, 0.5, 1.0, 2.0);

      vec3 i  = floor(v + dot(v, C.yyy));
      vec3 x0 = v - i + dot(i, C.xxx);

      vec3 g = step(x0.yzx, x0.xyz);
      vec3 l = 1.0 - g;
      vec3 i1 = min( g.xyz, l.zxy );
      vec3 i2 = max( g.xyz, l.zxy );

      vec3 x1 = x0 - i1 + C.xxx;
      vec3 x2 = x0 - i2 + C.yyy;
      vec3 x3 = x0 - D.yyy;

      i = mod289(i);
      vec4 p = permute( permute( permute(
                 i.z + vec4(0.0, i1.z, i2.z, 1.0 ))
               + i.y + vec4(0.0, i1.y, i2.y, 1.0 ))
               + i.x + vec4(0.0, i1.x, i2.x, 1.0 ));

      float n_ = 0.142857142857;
      vec3  ns = n_ * D.wyz - D.xzx;

      vec4 j = p - 49.0 * floor(p * ns.z * ns.z);

      vec4 x_ = floor(j * ns.z);
      vec4 y_ = floor(j - 7.0 * x_ );

      vec4 x = x_ *ns.x + ns.yyyy;
      vec4 y = y_ *ns.x + ns.yyyy;
      vec4 h = 1.0 - abs(x) - abs(y);

      vec4 b0 = vec4( x.xy, y.xy );
      vec4 b1 = vec4( x.zw, y.zw );

      vec4 s0 = floor(b0)*2.0 + 1.0;
      vec4 s1 = floor(b1)*2.0 + 1.0;
      vec4 sh = -step(h, vec4(0.0));

      vec4 a0 = b0.xzyw + s0.xzyw*sh.xxyy ;
      vec4 a1 = b1.xzyw + s1.xzyw*sh.zzww ;

      vec3 p0 = vec3(a0.xy,h.x);
      vec3 p1 = vec3(a0.zw,h.y);
      vec3 p2 = vec3(a1.xy,h.z);
      vec3 p3 = vec3(a1.zw,h.w);

      vec4 norm = taylorInvSqrt(vec4(dot(p0,p0), dot(p1,p1), dot(p2, p2), dot(p3,p3)));
      p0 *= norm.x;
      p1 *= norm.y;
      p2 *= norm.z;
      p3 *= norm.w;

      vec4 m = max(0.6 - vec4(dot(x0,x0), dot(x1,x1), dot(x2,x2), dot(x3,x3)), 0.0);
      m = m * m;
      return 42.0 * dot( m*m, vec4( dot(p0,x0), dot(p1,x1), dot(p2,x2), dot(p3,x3) ) );
    }

    void main() {
      vec3 viewDir = normalize(vViewPosition);
      vec3 normal = normalize(vNormal);

      // 1. Animate noise to drive organic flowing pattern
      float noiseFreq = 1.2;
      vec3 noisePos = vWorldPosition * noiseFreq + uNoiseOffset;
      float n = snoise(noisePos) * 0.5 + 0.5; // map from [-1, 1] to [0, 1]

      // 2. Mix colors via smoothstep bands
      float mix1 = smoothstep(0.1, 0.6, n);
      float mix2 = smoothstep(0.4, 0.9, n);
      
      vec3 baseColor = mix(uColorA, uColorB, mix1);
      baseColor = mix(baseColor, uColorC, mix2);

      // 3. Fresnel for the bright glassy rim glow
      float fresnelDot = max(dot(normal, viewDir), 0.0);
      float fresnel = pow(1.0 - fresnelDot, 2.5);
      vec3 rimColor = vec3(1.0); // White/bright glow at edges
      baseColor += rimColor * fresnel * uFresnelIntensity;

      // 4. Subtle specular highlight
      vec3 lightDir = normalize(vec3(1.0, 1.5, 1.0)); 
      vec3 halfVector = normalize(lightDir + viewDir);
      float specularDot = max(dot(normal, halfVector), 0.0);
      float specular = pow(specularDot, 64.0); // High exponent for a sharp hotspot
      baseColor += vec3(1.0) * specular * uSpecularIntensity;

      // 5. Fresnel-driven opacity falloff at the very edge
      float alpha = smoothstep(0.0, 0.3, fresnelDot) * 0.95 + 0.05;

      gl_FragColor = vec4(baseColor, alpha);
      
      // Basic tone mapping compatibility
      #include <tonemapping_fragment>
      #include <colorspace_fragment>
    }
  `
);

const HaloMaterial = shaderMaterial(
  { uColor: new THREE.Color("#b06bff"), uBloomIntensity: 0.6 },
  `varying vec2 vUv; void main() { vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`,
  `
    uniform vec3 uColor;
    uniform float uBloomIntensity;
    varying vec2 vUv;
    void main() {
      float dist = distance(vUv, vec2(0.5));
      // Multi-layered smoothstep for a beautiful bloom falloff
      float core = smoothstep(0.15, 0.0, dist);
      float mid = smoothstep(0.3, 0.1, dist) * 0.6;
      float outer = smoothstep(0.5, 0.2, dist) * 0.3;
      
      float alpha = (core + mid + outer) * uBloomIntensity;
      gl_FragColor = vec4(uColor, alpha);
      #include <tonemapping_fragment>
      #include <colorspace_fragment>
    }
  `
);

extend({ OrbMaterial, HaloMaterial });

// --------------------------------------------------------
// DEFAULT CONFIGURATION
// --------------------------------------------------------

const ORB_CONFIG = {
  colorA: "#ff4fd8", // primary / hot pink
  colorB: "#5b8cff", // secondary / blue
  colorC: "#b06bff", // tertiary / purple
};

// --------------------------------------------------------
// COMPONENT
// --------------------------------------------------------

export default function GradientOrb({ 
  colors = ORB_CONFIG, 
  size = 1, 
  state = "idle", 
  audioLevel = 0,
  autoRotate = false 
}) {
  const meshRef = useRef();
  const orbMaterialRef = useRef();
  const haloMaterialRef = useRef();
  
  // Track visibility to pause the render loop if off-screen
  const [isVisible, setIsVisible] = useState(true);

  // Memoize Three.js Color objects
  const targetColors = state === 'sleeping' ? {
    colorA: "#1a1a24", // dark navy
    colorB: "#2b2b36", // gray blue
    colorC: "#0f0f15"  // very dark gray
  } : colors;

  const colorA = useMemo(() => new THREE.Color(targetColors.colorA), [targetColors.colorA]);
  const colorB = useMemo(() => new THREE.Color(targetColors.colorB), [targetColors.colorB]);
  const colorC = useMemo(() => new THREE.Color(targetColors.colorC), [targetColors.colorC]);

  // Centralized state parameters for lerping
  const params = useRef({
    flowSpeed: 0.15,
    scale: 1.0,
    fresnelIntensity: 0.7,
    specularIntensity: 0.8,
    bloomIntensity: 0.6,
    flowDir: new THREE.Vector3(0.8, 1.0, 0.5),
    noiseOffset: new THREE.Vector3(0, 0, 0)
  });
  // === ANIMATION LOOP ===
  useFrame((clockState, delta) => {
    if (!isVisible) return; 
    
    try {
      const time = clockState.clock.elapsedTime;
      const p = params.current;
      
      // 1. Determine targets based on current 'state' and 'audioLevel'
      let tFlowSpeed = 0.15;
      let tScale = 1.0;
      let tFresnel = 0.7;
      let tSpecular = 0.8;
      let tBloom = 0.6;
      const tFlowDir = new THREE.Vector3(0.8, 1.0, 0.5);

      if (state === 'listening') {
        tFlowSpeed = 0.15 * 1.3;
        tScale = 1.0 + Math.sin(time * 1.5) * 0.02; // Gentle breathing
        tFresnel = 0.85; // Brightens slightly
        tBloom = 0.8;
      } else if (state === 'speaking') {
        // Fallback synthetic pulse if no audio data is provided
        const activeAudio = audioLevel > 0 ? audioLevel : Math.max(0, Math.sin(time * 5.0) * 0.5);
        tFlowSpeed = 0.15 + (activeAudio * 1.0);
        tScale = 1.0 + (activeAudio * 0.08);
        tFresnel = 0.7 + (activeAudio * 0.4);
        tSpecular = 0.8 + (activeAudio * 0.5);
        tBloom = 0.6 + (activeAudio * 0.5);
      } else if (state === 'thinking') {
        tFlowSpeed = 0.25; // Moderate constant pulse
        tFresnel = 0.75;
        tBloom = 0.7;
        tFlowDir.set(2.0, 0.0, 0.0); // Bias along +X for directional processing flow
      } else if (state === 'sleeping') {
        tFlowSpeed = 0.005; // Extremely slow flow, essentially paused
        tScale = 0.95; // Shrink slightly
        tFresnel = 0.2; // Dim rim light
        tBloom = 0.1; // Minimal glow
        tSpecular = 0.1; // Dull surface
      }

      // 2. Smoothly interpolate current params towards targets
      const lerpSpeed = 5.0; // speed of transition between states
      p.flowSpeed = THREE.MathUtils.lerp(p.flowSpeed, tFlowSpeed, delta * lerpSpeed);
      p.scale = THREE.MathUtils.lerp(p.scale, tScale, delta * lerpSpeed);
      p.fresnelIntensity = THREE.MathUtils.lerp(p.fresnelIntensity, tFresnel, delta * lerpSpeed);
      p.specularIntensity = THREE.MathUtils.lerp(p.specularIntensity, tSpecular, delta * lerpSpeed);
      p.bloomIntensity = THREE.MathUtils.lerp(p.bloomIntensity, tBloom, delta * lerpSpeed);
      p.flowDir.lerp(tFlowDir, delta * 2.0); // slower directional transition

      // 3. Accumulate noise offset based on smoothed flow speed and direction
      const step = p.flowSpeed * delta;
      p.noiseOffset.add(p.flowDir.clone().multiplyScalar(step));

      // 4. Update material uniforms
      if (orbMaterialRef.current) {
        orbMaterialRef.current.uNoiseOffset.copy(p.noiseOffset);
        orbMaterialRef.current.uFresnelIntensity = p.fresnelIntensity;
        orbMaterialRef.current.uSpecularIntensity = p.specularIntensity;
      }
      
      if (haloMaterialRef.current) {
        haloMaterialRef.current.uBloomIntensity = p.bloomIntensity;
      }

      // Apply scale
      if (meshRef.current) {
        meshRef.current.scale.setScalar(size * p.scale);
      }
    } catch (e) {
      console.error("Error in GradientOrb useFrame:");
      console.error(e?.message || String(e));
    }
  });

  return (
    <group>
      {/* 1. BACKGROUND HALO */}
      <mesh position={[0, 0, -1]} scale={[size * 4.5, size * 4.5, 1]}>
        <planeGeometry args={[1, 1]} />
        <haloMaterial 
          ref={haloMaterialRef}
          uColor={colorC} 
          transparent 
          depthWrite={false} 
          blending={THREE.AdditiveBlending}
        />
      </mesh>

      {/* 2. GLOSSY ORB */}
      <mesh ref={meshRef} scale={size}>
        <sphereGeometry args={[1, 64, 64]} />
        <orbMaterial
          ref={orbMaterialRef}
          uColorA={colorA}
          uColorB={colorB}
          uColorC={colorC}
          transparent={true}
          depthWrite={false}
        />
      </mesh>

      {/* 3. SCENE LIGHTING & ENVIRONMENT */}
      <Environment preset="studio" />
      <ambientLight intensity={0.2} />
      <directionalLight position={[2, 3, 2]} intensity={0.4} />

      {/* 5. CONTROLS */}
      {autoRotate && <OrbitControls enableZoom={false} />}
    </group>
  );
}
