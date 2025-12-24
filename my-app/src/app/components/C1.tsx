import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { CheckCircle } from "lucide-react";

export default function C1() {
  const tasks = [
    { id: 1, title: "Complete initial setup", completed: true },
    { id: 2, title: "Navigate to primary interface", completed: true },
    { id: 3, title: "Execute task sequence A", completed: false },
    { id: 4, title: "Record observations", completed: false },
  ];

  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <h1>Condition 1 (C1)</h1>
        <p className="text-muted-foreground">
          In this condition, you will interact with the baseline version of the system. Please follow the tasks outlined below in order.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Badge variant="secondary">Baseline</Badge>
              Condition Details
            </CardTitle>
            <CardDescription>
              Standard interface configuration without enhancements
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span>Interface Type:</span>
                <Badge>Standard UI</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span>Assistance Level:</span>
                <Badge variant="outline">Minimal</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span>Task Complexity:</span>
                <Badge variant="secondary">Medium</Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Task Progress</CardTitle>
            <CardDescription>
              Complete each task in sequence
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {tasks.map((task) => (
                <div key={task.id} className="flex items-center gap-3 p-2 rounded border">
                  <CheckCircle 
                    className={`h-5 w-5 ${task.completed ? 'text-green-600' : 'text-muted-foreground'}`} 
                  />
                  <span className={task.completed ? 'line-through text-muted-foreground' : ''}>
                    {task.title}
                  </span>
                  {task.completed && <Badge className="ml-auto">Done</Badge>}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Instructions</CardTitle>
          <CardDescription>
            Please read carefully before beginning
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <ol className="list-decimal list-inside space-y-2">
            <li>Take your time to familiarize yourself with the interface</li>
            <li>Complete each task at your own pace</li>
            <li>Think aloud during the process if comfortable</li>
            <li>Ask for clarification if needed</li>
          </ol>
          
          <div className="flex gap-3 pt-4">
            <Button>Start Condition 1</Button>
            <Button variant="outline">Review Instructions</Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}