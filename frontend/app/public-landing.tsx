'use client';

import { useEffect, useState, type FormEvent } from 'react';
import { ArrowRight, Moon, Sun } from 'lucide-react';

type Opportunity = { id:string; title:string; organization:string; location:string; category:string; description:string };
type Course = { id:string; title:string; category:string; lessons:number };
type Workshop = { id:string; title:string; date:string; format:string; seats:number };
type Props = {
  onSignIn:(event:FormEvent<HTMLFormElement>)=>void;
  onSignUp:(event:FormEvent<HTMLFormElement>)=>void;
  name:string; setName:(value:string)=>void;
  email:string; setEmail:(value:string)=>void;
  password:string; setPassword:(value:string)=>void;
  loginError:string; darkTheme:boolean; toggleTheme:()=>void;
  opportunities:Opportunity[]; courses:Course[]; workshops:Workshop[];
};

export default function SikshaLanding({onSignIn,onSignUp,name,setName,email,setEmail,password,setPassword,loginError,darkTheme,toggleTheme,opportunities,courses,workshops}:Props){
  const [authMode,setAuthMode]=useState<'signin'|'signup'>('signin');
  useEffect(()=>{
    const reducedMotion=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const coarsePointer=window.matchMedia('(pointer: coarse)').matches;
    if(reducedMotion||coarsePointer)return;
    const first=document.querySelector<HTMLElement>('.siksha-bg-one');
    const second=document.querySelector<HTMLElement>('.siksha-bg-two');
    let targetX=0,targetY=0,currentX=0,currentY=0,frame=0;
    const move=(event:MouseEvent)=>{targetX=(event.clientX/window.innerWidth-.5)*2;targetY=(event.clientY/window.innerHeight-.5)*2;if(!frame)frame=requestAnimationFrame(tick);};
    const leave=()=>{targetX=0;targetY=0;if(!frame)frame=requestAnimationFrame(tick);};
    function tick(){
      currentX+=(targetX-currentX)*.07;currentY+=(targetY-currentY)*.07;
      if(first)first.style.transform=`translateX(-50%) perspective(1400px) rotateY(${(currentX*16).toFixed(2)}deg) rotateX(${(-currentY*9).toFixed(2)}deg) translate3d(${(-currentX*26).toFixed(1)}px,${(-currentY*14).toFixed(1)}px,0) scale(1.05)`;
      if(second)second.style.transform=`translate(-50%,-50%) perspective(1400px) rotateY(${(-currentX*9).toFixed(2)}deg) rotateX(${(currentY*5).toFixed(2)}deg) translate3d(${(currentX*34).toFixed(1)}px,${(currentY*18).toFixed(1)}px,0)`;
      frame=0;
      if(Math.abs(targetX-currentX)>.01||Math.abs(targetY-currentY)>.01)frame=requestAnimationFrame(tick);
    }
    window.addEventListener('mousemove',move);document.addEventListener('mouseleave',leave);
    return()=>{window.removeEventListener('mousemove',move);document.removeEventListener('mouseleave',leave);cancelAnimationFrame(frame);};
  },[]);
  return <main className="siksha-site" id="top">
    <div className="siksha-bg siksha-bg-one" aria-hidden="true"/>
    <header className="siksha-header">
      <div className="siksha-nav-shell">
        <a className="siksha-company-brand" href="#top" aria-label="Tech & Trend Media Pvt. Ltd. — Siksha home"><img src="/tech-trend-logo.png" alt="Tech & Trend Media logo"/><span><strong>Tech &amp; Trend Media Pvt. Ltd.</strong><small>Siksha learning platform</small></span></a>
        <nav className="siksha-nav" aria-label="Main navigation">
          <a href="#about">About Us</a><a href="#paths">Workshops</a><a href="#enquiry">Forms</a><a href="#contacts">Contacts</a>
        </nav>
        <div className="siksha-nav-actions">
          <button className="siksha-theme-toggle" onClick={toggleTheme} aria-label={darkTheme?'Switch to light theme':'Switch to dark theme'} title={darkTheme?'Switch to light theme':'Switch to dark theme'}>{darkTheme?<Sun size={17}/>:<Moon size={17}/>}</button>
          <a className="siksha-signin-link" href="#signin">Sign in</a><a className="siksha-pill siksha-nav-portal" href="#signin">Student portal</a>
        </div>
      </div>
    </header>

    <section className="siksha-hero siksha-section" aria-labelledby="hero-title">
      <h1 id="hero-title">Learn by doing.<br/><em>Grow by guiding.</em></h1>
      <p>Arise, awake, and stop not till the goal is reached. <span>— Swami Vivekananda</span></p>
      <div className="siksha-hero-actions"><a className="siksha-pill" href="#paths">Explore paths</a><a className="siksha-chip" href="#enquiry">Register interest</a></div>
    </section>

    <section className="siksha-showcase siksha-section" aria-label="Explore learning paths">
      <div className="siksha-showcase-image" role="img" aria-label="A green illustration representing learning, technology and growth"/>
      <div className="siksha-search-card"><span>Which path are you looking for?</span><div><span>Internship, learning or workshop</span><a className="siksha-pill siksha-arrow-pill" href="#paths" aria-label="Explore paths"><ArrowRight size={17}/></a></div></div>
      <div className="siksha-showcase-chips"><a className="siksha-chip" href="#internships">Internship &amp; training</a><a className="siksha-chip" href="#learning">Learning</a><a className="siksha-chip" href="#workshops">Workshops &amp; mentorship</a></div>
    </section>
    <p className="siksha-mantra">Learn · Build · Mentor · Grow · Share · Certify</p>

    <section id="paths" className="siksha-section siksha-content-section">
      <div className="siksha-section-heading"><h2>Your path through <em>Siksha.</em></h2><p>Three ways to turn learning into experience. Choose one to see what is open.</p></div>
      <div className="siksha-card-grid">
        <article id="internships" className="siksha-card"><span className="siksha-card-number">01</span><h3>Internship &amp; training</h3><p>{opportunities[0]?`${opportunities.length} opportunities, including ${opportunities[0].title}.`: 'Guided placements and skill tracks with mentor check-ins.'}</p><a href="#signin">Explore <ArrowRight size={15}/></a></article>
        <article id="learning" className="siksha-card"><span className="siksha-card-number">02</span><h3>Learning paths</h3><p>{courses[0]?`${courses.length} guided courses, including ${courses[0].title}.`:'Build practical skills at your own pace with guided courses.'}</p><a href="#signin">Explore <ArrowRight size={15}/></a></article>
        <article id="workshops" className="siksha-card"><span className="siksha-card-number">03</span><h3>Workshops &amp; mentorship</h3><p>{workshops[0]?`${workshops.length} upcoming sessions, including ${workshops[0].title}.`:'Hands-on sessions and one-to-one guidance to help you grow.'}</p><a href="#signin">Explore <ArrowRight size={15}/></a></article>
      </div>
    </section>

    <section id="about" className="siksha-section siksha-content-section siksha-about-section">
      <div className="siksha-section-heading"><h2>Made to <em>guide you.</em></h2></div>
      <div className="siksha-card-grid">
        <article className="siksha-card"><h3>Learn on real work</h3><p>Explore opportunities that help turn classroom concepts into professional practice.</p></article>
        <article className="siksha-card"><h3>Guided by mentors</h3><p>Get thoughtful feedback and support from people who have done the work.</p></article>
        <article className="siksha-card"><h3>Progress you can see</h3><p>Follow your learning, applications and internship journey in your workspace.</p></article>
      </div>
    </section>

    <section id="signin" className="siksha-section siksha-signin-section">
      <div className="siksha-bg siksha-bg-two" aria-hidden="true"/>
      <div className="siksha-section-heading"><h2>Pick up <em>where you left off.</em></h2><p>Sign in to continue your learning, internship or workshop journey.</p></div>
      <form className="siksha-form siksha-login-form" onSubmit={authMode==='signin'?onSignIn:onSignUp}>
        <h3>{authMode==='signin'?'Welcome back.':'Create your account.'}</h3>
        {authMode==='signup'&&<label className="siksha-field"><span>Full name</span><input autoComplete="name" value={name} onChange={event=>setName(event.target.value)} minLength={2} required/></label>}
        <label className="siksha-field"><span>Email</span><input autoComplete="username" type="email" value={email} onChange={event=>setEmail(event.target.value)} required/></label>
        <label className="siksha-field"><span>Password</span><input autoComplete={authMode==='signin'?'current-password':'new-password'} type="password" value={password} onChange={event=>setPassword(event.target.value)} minLength={authMode==='signup'?8:1} required/></label>
        {loginError&&<p className="siksha-form-error" role="alert">{loginError}</p>}
        <button className="siksha-pill siksha-form-submit" type="submit">{authMode==='signin'?'Sign in':'Create account'} <ArrowRight size={16}/></button>
        <button className="siksha-secondary-link" type="button" onClick={()=>setAuthMode(authMode==='signin'?'signup':'signin')}>{authMode==='signin'?'New here? Create an account':'Already have an account? Sign in'}</button>
        <details className="siksha-demo-accounts"><summary>Local demo accounts</summary><span>Choose a role to fill its development credentials.</span><div><button type="button" onClick={()=>{setEmail('student@demo.local');setPassword('StudentDemo!2026');}}>Candidate</button><button type="button" onClick={()=>{setEmail('admin@demo.local');setPassword('AdminDemo!2026');}}>Organization admin</button><button type="button" onClick={()=>{setEmail('mentor@demo.local');setPassword('MentorDemo!2026');}}>Mentor</button></div></details>
      </form>
    </section>

    <section id="contacts" className="siksha-section siksha-contact-section">
      <div><h2>Begin with <em>one good question.</em></h2><p>Explore the programme catalogue or sign in to connect with your learning community.</p><div className="siksha-contact-links"><a href="#paths">Browse learning paths <ArrowRight size={15}/></a><a href="#signin">Go to student portal <ArrowRight size={15}/></a></div></div>
      <div id="enquiry" className="siksha-form siksha-enquiry-card"><span className="siksha-kicker">ENQUIRY &amp; REGISTRATION</span><h3>Ready to get started?</h3><p>Find an opportunity, join a workshop or continue a course from your student workspace.</p><a className="siksha-pill" href="#signin">Sign in to continue <ArrowRight size={16}/></a><a className="siksha-secondary-link" href="#paths">Explore the available paths</a></div>
    </section>

    <footer className="siksha-footer siksha-section"><a className="siksha-footer-brand" href="#top"><img src="/tech-trend-logo.png" alt=""/><span><strong>Tech &amp; Trend Media Pvt. Ltd.</strong><small>Siksha · Learning, connected to experience.</small><small>Sanjay Palace, Agra</small></span></a><a href="#contacts">Questions? Start here <ArrowRight size={14}/></a></footer>
  </main>;
}
