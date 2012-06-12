package edu.uci.ics;

import org.eclipse.jdt.core.dom.MethodDeclaration;

import edu.cmu.cs.crystal.AbstractCrystalMethodAnalysis;

public class NullPointerAnalysis extends AbstractCrystalMethodAnalysis {

	@Override
	public void analyzeMethod(MethodDeclaration arg0) {
		// TODO Auto-generated method stub

	}

	@Override
	public String getName() {
		return "Check for NPEs";
	}

}
