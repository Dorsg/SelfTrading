<template>
    <div class="controls">
      <button class="primary" @click="$emit('openForm')">➕ Create Runner</button>
    </div>
  </template>
  
  <style scoped>
  .controls {
    margin-bottom: 20px;
  }
  button.primary {
    background-color: #00d1b2;
    color: #1e1e2f;
    border: none;
    padding: 10px 20px;
    font-weight: bold;
    border-radius: 6px;
    cursor: pointer;
    transition: background-color 0.2s ease;
  }
  button.primary:hover {
    background-color: #00b89c;
  }
  </style>
  