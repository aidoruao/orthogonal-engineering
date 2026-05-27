import Mathlib.Data.ZMod.Basic
import Mathlib.Data.Nat.ModEq

open System

def main : IO Unit := do
  let env ← getEnv
  for (name, _) in env.constants.toList do
    if name.toString.startsWith "Mathlib.Data.ZMod.Basic" 
       || name.toString.startsWith "ZMod" 
       || name.toString.startsWith "Nat.ModEq" then
      IO.println name.toString
    if name.toString.startsWith "Nat" && name.toString.contains "mod" then
      IO.println name.toString
    if name.toString.startsWith "Nat" && name.toString.contains "ModEq" then
      IO.println name.toString
