'use client';
import { useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "./components/ui/card";
import { Button } from "./components/ui/button";
import { Badge } from "./components/ui/badge";
import { Music, Home } from "lucide-react";

export default function App() {
  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="h-8 w-8 bg-primary rounded-lg flex items-center justify-center">
              <Music className="h-5 w-5 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-xl">
                Violin Practice Studio
              </h1>
              <p className="text-sm text-muted-foreground">
                Interactive Learning Platform
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-8">
        <div className="max-w-6xl mx-auto">
          <div className="space-y-8">
            {/* Welcome Section */}
            <div className="text-center space-y-4">
              <div className="flex justify-center">
                <div className="h-16 w-16 bg-primary rounded-full flex items-center justify-center">
                  <Music className="h-8 w-8 text-primary-foreground" />
                </div>
              </div>
              <div className="space-y-2">
                <h1 className="text-3xl">
                  Welcome to Violin Practice
                </h1>
                <p className="text-muted-foreground max-w-2xl mx-auto">
                  Please follow the instructions of the
                  researchers.
                </p>
              </div>
            </div>

            {/* Navigation Cards */}
            <div className="grid gap-6 md:grid-cols-2 max-w-4xl mx-auto">
              <Card className="cursor-pointer transition-all duration-200 bg-blue-50 hover:bg-blue-100 border-blue-200 hover:shadow-lg">
                <CardHeader className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="h-12 w-12 rounded-lg bg-white/50 flex items-center justify-center">
                      <Home className="h-6 w-6 text-blue-600" />
                    </div>
                    <Badge
                      variant="secondary"
                      className="text-xs"
                    >
                      1
                    </Badge>
                  </div>
                  <div className="space-y-2">
                    <CardTitle className="text-xl">
                      Level Assessment
                    </CardTitle>
                    <CardDescription className="text-sm">
                      Evaluate your violin playing skills and
                      technique
                    </CardDescription>
                  </div>
                </CardHeader>
                <CardContent>
                  <Button
                    variant="outline"
                    className="w-full bg-white/50 hover:bg-white/70"
                  >
                    Start Session
                  </Button>
                </CardContent>
              </Card>

              <Card className="cursor-pointer transition-all duration-200 bg-green-50 hover:bg-green-100 border-green-200 hover:shadow-lg">
                <CardHeader className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="h-12 w-12 rounded-lg bg-white/50 flex items-center justify-center">
                      <Home className="h-6 w-6 text-green-600" />
                    </div>
                    <Badge
                      variant="secondary"
                      className="text-xs"
                    >
                      2
                    </Badge>
                  </div>
                  <div className="space-y-2">
                    <CardTitle className="text-xl">
                      Condition 1
                    </CardTitle>
                    <CardDescription className="text-sm">
                      Condition 1
                    </CardDescription>
                  </div>
                </CardHeader>
                <CardContent>
                  <Button
                    variant="outline"
                    className="w-full bg-white/50 hover:bg-white/70"
                  >
                    Start Session
                  </Button>
                </CardContent>
              </Card>

              <Card className="cursor-pointer transition-all duration-200 bg-purple-50 hover:bg-purple-100 border-purple-200 hover:shadow-lg">
                <CardHeader className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="h-12 w-12 rounded-lg bg-white/50 flex items-center justify-center">
                      <Home className="h-6 w-6 text-purple-600" />
                    </div>
                    <Badge
                      variant="secondary"
                      className="text-xs"
                    >
                      3
                    </Badge>
                  </div>
                  <div className="space-y-2">
                    <CardTitle className="text-xl">
                      Condition 2
                    </CardTitle>
                    <CardDescription className="text-sm">
                      Condition 2
                    </CardDescription>
                  </div>
                </CardHeader>
                <CardContent>
                  <Button
                    variant="outline"
                    className="w-full bg-white/50 hover:bg-white/70"
                  >
                    Start Session
                  </Button>
                </CardContent>
              </Card>

              <Card className="cursor-pointer transition-all duration-200 bg-orange-50 hover:bg-orange-100 border-orange-200 hover:shadow-lg">
                <CardHeader className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="h-12 w-12 rounded-lg bg-white/50 flex items-center justify-center">
                      <Music className="h-6 w-6 text-orange-600" />
                    </div>
                    <Badge
                      variant="secondary"
                      className="text-xs"
                    >
                      4
                    </Badge>
                  </div>
                  <div className="space-y-2">
                    <CardTitle className="text-xl">
                      Performance
                    </CardTitle>
                    <CardDescription className="text-sm">
                      View and practice with interactive music
                      scores
                    </CardDescription>
                  </div>
                </CardHeader>
                <CardContent>
                  <Button
                    variant="outline"
                    className="w-full bg-white/50 hover:bg-white/70"
                  >
                    Start Session
                  </Button>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t bg-muted/20 mt-12">
        <div className="container mx-auto px-6 py-6">
          <div className="text-center text-sm text-muted-foreground">
            © Nil Ponsa 2025 | Violin Practice Studio
          </div>
        </div>
      </footer>
    </div>
  );
}