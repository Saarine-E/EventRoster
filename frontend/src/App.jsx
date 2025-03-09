import { useState, useEffect, useRef } from 'react'
import './App.css'
import { Routes, Route } from "react-router";
import Layout from './views/Layout';
import Homepage from './views/Homepage';
import Settings from './views/Settings';

function App() {

  return (
    <>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Homepage />} />
          <Route path="/settings" element={<Settings />} />
        </Route>
      </Routes>
    </>
  )
}

export default App
