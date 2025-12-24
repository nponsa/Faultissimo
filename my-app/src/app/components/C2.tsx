import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { CheckCircle, Zap } from "lucide-react";

export default function C2() {
  const tasks = [
    { id: 1, title: "Initialize enhanced interface", completed: false },
    { id: 2, title: "Explore adaptive features", completed: false },
    { id: 3, title: "Execute task sequence B", completed: false },
    { id: 4, title: "Compare with C1 experience", completed: false },
  ];

  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <h1>Condition 2 (C2)</h1>
        <p className="text-muted-foreground">
          In this condition, you will interact with the enhanced version of the system featuring improved user interface elements and assistance features.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Badge className="bg-blue-600">Enhanced</Badge>
              <Zap className="h-4 w-4" />
              Condition Details
            </CardTitle>
            <CardDescription>
              Improved interface with enhanced user assistance
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span>Interface Type:</span>
                <Badge className="bg-blue-600">Enhanced UI</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span>Assistance Level:</span>
                <Badge variant="default">High</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span>Task Complexity:</span>
                <Badge variant="secondary">Medium</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span>Adaptive Features:</span>
                <Badge variant="outline">Enabled</Badge>
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
          <CardTitle>Enhanced Features</CardTitle>
          <CardDescription>
            New capabilities available in this condition
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <h4>Interface Improvements</h4>
              <ul className="text-sm space-y-1 text-muted-foreground">
                <li>• Contextual help tooltips</li>
                <li>• Smart navigation assistance</li>
                <li>• Visual feedback enhancements</li>
                <li>• Streamlined workflow</li>
              </ul>
            </div>
            <div className="space-y-2">
              <h4>Adaptive Elements</h4>
              <ul className="text-sm space-y-1 text-muted-foreground">
                <li>• Personalized recommendations</li>
                <li>• Dynamic interface adjustments</li>
                <li>• Progressive disclosure</li>
                <li>• Error prevention features</li>
              </ul>
            </div>
          </div>
          
          <div className="flex gap-3 pt-4">
            <Button>Start Condition 2</Button>
            <Button variant="outline">Compare Conditions</Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}