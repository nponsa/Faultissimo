import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Progress } from "./ui/progress";
import { Textarea } from "./ui/textarea";
import { Label } from "./ui/label";
import { RadioGroup, RadioGroupItem } from "./ui/radio-group";
import { useState } from "react";

export default function Assessment() {
  const [progress, setProgress] = useState(25);
  const [responses, setResponses] = useState({
    question1: "",
    question2: "",
    feedback: ""
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Handle form submission
    console.log("Assessment submitted:", responses);
  };

  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <h1>Assessment</h1>
        <p className="text-muted-foreground">
          Please complete the following assessment questions. Your responses will help us understand your experience with the system.
        </p>
      </div>

      <div className="space-y-2">
        <Label>Assessment Progress</Label>
        <Progress value={progress} className="w-full" />
        <p className="text-sm text-muted-foreground">{progress}% complete</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>User Experience Assessment</CardTitle>
          <CardDescription>
            Answer the following questions based on your interaction with the system.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-3">
              <Label>1. How would you rate the overall usability of the system?</Label>
              <RadioGroup
                value={responses.question1}
                onValueChange={(value) => setResponses(prev => ({ ...prev, question1: value }))}
              >
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="excellent" id="excellent" />
                  <Label htmlFor="excellent">Excellent</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="good" id="good" />
                  <Label htmlFor="good">Good</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="fair" id="fair" />
                  <Label htmlFor="fair">Fair</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="poor" id="poor" />
                  <Label htmlFor="poor">Poor</Label>
                </div>
              </RadioGroup>
            </div>

            <div className="space-y-3">
              <Label>2. Did you encounter any difficulties during the tasks?</Label>
              <RadioGroup
                value={responses.question2}
                onValueChange={(value) => setResponses(prev => ({ ...prev, question2: value }))}
              >
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="none" id="none" />
                  <Label htmlFor="none">No difficulties</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="minor" id="minor" />
                  <Label htmlFor="minor">Minor difficulties</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="major" id="major" />
                  <Label htmlFor="major">Major difficulties</Label>
                </div>
              </RadioGroup>
            </div>

            <div className="space-y-3">
              <Label htmlFor="feedback">3. Please provide any additional feedback or suggestions:</Label>
              <Textarea
                id="feedback"
                placeholder="Share your thoughts about the system..."
                value={responses.feedback}
                onChange={(e) => setResponses(prev => ({ ...prev, feedback: e.target.value }))}
                className="min-h-[100px]"
              />
            </div>

            <div className="flex gap-3">
              <Button type="submit">Submit Assessment</Button>
              <Button 
                type="button" 
                variant="outline"
                onClick={() => setProgress(Math.min(progress + 25, 100))}
              >
                Next Question
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}