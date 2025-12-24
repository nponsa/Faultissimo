import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { Progress } from "./ui/progress";
import { Music, Play, Pause, RotateCcw, Volume2, Metronome, Star } from "lucide-react";
import { useState } from "react";

export default function Performance() {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentMeasure, setCurrentMeasure] = useState(1);
  const [tempo, setTempo] = useState(120);

  const musicPieces = [
    {
      title: "Twinkle, Twinkle, Little Star",
      composer: "Traditional",
      difficulty: "Beginner",
      measures: 8,
      key: "G Major",
      timeSignature: "4/4",
      completed: true,
      score: 95
    },
    {
      title: "Ode to Joy",
      composer: "L. van Beethoven",
      difficulty: "Intermediate",
      measures: 16,
      key: "D Major", 
      timeSignature: "4/4",
      completed: false,
      score: 0
    },
    {
      title: "Canon in D",
      composer: "J. Pachelbel",
      difficulty: "Advanced",
      measures: 32,
      key: "D Major",
      timeSignature: "4/4",
      completed: false,
      score: 0
    }
  ];

  const recentPractice = [
    { piece: "Twinkle, Twinkle, Little Star", date: "Today", duration: "15 min", accuracy: 95 },
    { piece: "Ode to Joy", date: "Yesterday", duration: "22 min", accuracy: 78 },
    { piece: "Scale Practice", date: "2 days ago", duration: "10 min", accuracy: 92 },
  ];

  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <h1>Performance &amp; Sheet Music</h1>
        <p className="text-muted-foreground">
          Practice with interactive sheet music and track your performance progress.
        </p>
      </div>

      {/* Interactive Music Player */}
      <Card className="bg-gradient-to-r from-blue-50 to-purple-50 border-blue-200">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Music className="h-5 w-5" />
            Now Playing: Twinkle, Twinkle, Little Star
          </CardTitle>
          <CardDescription>
            Traditional • G Major • 4/4 Time
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Music Score Representation */}
          <div className="bg-white rounded-lg p-6 border">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3>Sheet Music</h3>
                <Badge variant="secondary">Measure {currentMeasure} of 8</Badge>
              </div>
              
              {/* Simplified Staff Lines Representation */}
              <div className="relative h-32 bg-white rounded border">
                <div className="absolute inset-4">
                  {/* Staff lines */}
                  {[...Array(5)].map((_, i) => (
                    <div key={i} className="absolute w-full border-b border-gray-300" style={{ top: `${i * 20}%` }} />
                  ))}
                  
                  {/* Note representation */}
                  <div className="absolute top-1/2 left-8 transform -translate-y-1/2">
                    <div className="w-4 h-3 bg-black rounded-full"></div>
                  </div>
                  <div className="absolute top-1/2 left-20 transform -translate-y-1/2">
                    <div className="w-4 h-3 bg-black rounded-full"></div>
                  </div>
                  <div className="absolute top-1/3 left-32 transform -translate-y-1/2">
                    <div className="w-4 h-3 bg-black rounded-full"></div>
                  </div>
                  <div className="absolute top-1/3 left-44 transform -translate-y-1/2">
                    <div className="w-4 h-3 bg-black rounded-full"></div>
                  </div>
                </div>
              </div>

              {/* Progress Bar */}
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Progress</span>
                  <span>{Math.round((currentMeasure / 8) * 100)}%</span>
                </div>
                <Progress value={(currentMeasure / 8) * 100} className="h-2" />
              </div>
            </div>
          </div>

          {/* Playback Controls */}
          <div className="flex items-center justify-center gap-4">
            <Button 
              variant="outline" 
              size="sm"
              onClick={() => setCurrentMeasure(1)}
            >
              <RotateCcw className="h-4 w-4" />
            </Button>
            
            <Button 
              size="lg"
              onClick={() => setIsPlaying(!isPlaying)}
              className="h-12 w-12 rounded-full"
            >
              {isPlaying ? <Pause className="h-5 w-5" /> : <Play className="h-5 w-5" />}
            </Button>
            
            <div className="flex items-center gap-2">
              <Metronome className="h-4 w-4" />
              <span className="text-sm">{tempo} BPM</span>
            </div>
            
            <Button variant="outline" size="sm">
              <Volume2 className="h-4 w-4" />
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Music Library */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Music Library</CardTitle>
            <CardDescription>
              Choose a piece to practice
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {musicPieces.map((piece, index) => (
              <div key={index} className="flex items-center justify-between p-3 rounded-lg border bg-card hover:bg-accent/50 cursor-pointer">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <h4 className="font-medium">{piece.title}</h4>
                    {piece.completed && <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />}
                  </div>
                  <div className="text-sm text-muted-foreground">
                    {piece.composer} • {piece.key} • {piece.difficulty}
                  </div>
                </div>
                <div className="text-right space-y-1">
                  <Badge variant={piece.difficulty === 'Beginner' ? 'secondary' : piece.difficulty === 'Intermediate' ? 'default' : 'destructive'}>
                    {piece.difficulty}
                  </Badge>
                  {piece.completed && (
                    <div className="text-sm text-muted-foreground">{piece.score}%</div>
                  )}
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Recent Practice</CardTitle>
            <CardDescription>
              Your latest practice sessions
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {recentPractice.map((session, index) => (
              <div key={index} className="flex items-center justify-between p-3 rounded-lg border">
                <div className="space-y-1">
                  <h4 className="font-medium">{session.piece}</h4>
                  <div className="text-sm text-muted-foreground">
                    {session.date} • {session.duration}
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-sm font-medium">{session.accuracy}%</div>
                  <div className="text-xs text-muted-foreground">Accuracy</div>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      {/* Practice Statistics */}
      <Card>
        <CardHeader>
          <CardTitle>Performance Analytics</CardTitle>
          <CardDescription>
            Track your improvement over time
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-6 md:grid-cols-3">
            <div className="text-center space-y-2">
              <div className="text-3xl font-medium">92%</div>
              <div className="text-sm text-muted-foreground">Average Accuracy</div>
              <Progress value={92} className="h-2" />
            </div>
            <div className="text-center space-y-2">
              <div className="text-3xl font-medium">47</div>
              <div className="text-sm text-muted-foreground">Practice Sessions</div>
              <Progress value={75} className="h-2" />
            </div>
            <div className="text-center space-y-2">
              <div className="text-3xl font-medium">28h</div>
              <div className="text-sm text-muted-foreground">Total Practice Time</div>
              <Progress value={85} className="h-2" />
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}