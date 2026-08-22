import React from 'react';
import { motion } from 'motion/react';

export default function SplitText({ text, className = "", delay = 0 }) {
  const words = text.split(" ");
  
  return (
    <span className={`inline-block ${className}`}>
      {words.map((word, i) => (
        <motion.span
          key={i}
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: delay + i * 0.04, type: "spring", stiffness: 150 }}
          className="inline-block mr-[0.25em]"
        >
          {word}
        </motion.span>
      ))}
    </span>
  );
}
