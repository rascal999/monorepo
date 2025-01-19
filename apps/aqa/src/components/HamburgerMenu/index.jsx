import React from 'react';
import './styles.css';

const HamburgerMenu = ({ onClick }) => {
  return (
    <button className="hamburger-menu" onClick={onClick}>
      <div className="line"></div>
      <div className="line"></div>
      <div className="line"></div>
    </button>
  );
};

export default HamburgerMenu;
