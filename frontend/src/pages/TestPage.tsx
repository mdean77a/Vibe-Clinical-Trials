import React, { useState } from 'react';
import Button from '@/components/Button';
import Input from '@/components/Input';
import Textarea from '@/components/Textarea';
import Card from '@/components/Card';

const TestPage: React.FC = () => {
  const [inputValue, setInputValue] = useState('');
  const [textareaValue, setTextareaValue] = useState('');

  return (
    <div className="p-4 space-y-4">
      <Card>
        <h2 className="text-xl font-bold mb-2">Test Components</h2>
        <Button onClick={() => alert('Button clicked!')}>Click Me</Button>
      </Card>

      <Card>
        <Input
          placeholder="Type something..."
          value={inputValue}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => setInputValue(e.target.value)}
        />
      </Card>

      <Card>
        <Textarea
          placeholder="Type more..."
          value={textareaValue}
          onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setTextareaValue(e.target.value)}
        />
      </Card>
    </div>
  );
};

export default TestPage;
