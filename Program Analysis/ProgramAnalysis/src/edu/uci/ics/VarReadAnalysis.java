package edu.uci.ics;

import static org.eclipse.jdt.core.dom.ASTNode.FIELD_ACCESS;
import static org.eclipse.jdt.core.dom.ASTNode.SIMPLE_NAME;

import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.List;

import org.eclipse.jdt.core.ITypeRoot;
import org.eclipse.jdt.core.dom.ASTVisitor;
import org.eclipse.jdt.core.dom.ArrayAccess;
import org.eclipse.jdt.core.dom.Assignment;
import org.eclipse.jdt.core.dom.CompilationUnit;
import org.eclipse.jdt.core.dom.Expression;
import org.eclipse.jdt.core.dom.FieldAccess;
import org.eclipse.jdt.core.dom.FieldDeclaration;
import org.eclipse.jdt.core.dom.IBinding;
import org.eclipse.jdt.core.dom.IVariableBinding;
import org.eclipse.jdt.core.dom.InfixExpression;
import org.eclipse.jdt.core.dom.MethodDeclaration;
import org.eclipse.jdt.core.dom.MethodInvocation;
import org.eclipse.jdt.core.dom.Name;
import org.eclipse.jdt.core.dom.QualifiedName;
import org.eclipse.jdt.core.dom.SimpleName;
import org.eclipse.jdt.core.dom.VariableDeclarationFragment;
import org.eclipse.jdt.core.dom.VariableDeclarationStatement;

import edu.cmu.cs.crystal.AbstractCrystalMethodAnalysis;

public class VarReadAnalysis extends AbstractCrystalMethodAnalysis {

	private ReadCheckVisitor visitor;
	
	@Override
	public void beforeAllMethods(ITypeRoot compUnit, CompilationUnit rootNode) {
		visitor = new ReadCheckVisitor();
		rootNode.accept(visitor);
	}

	@Override
	public void analyzeMethod(MethodDeclaration d) {
	}

	@Override
	public void afterAllMethods(ITypeRoot compUnit, CompilationUnit rootNode) {
		List<IVariableBinding> allVars = visitor.getAllVars();
		PrintWriter pw = super.getReporter().userOut();
		if (allVars.size() > 0) {
			pw.println("The following variables are not read:");
			for (IVariableBinding binding : allVars)
				pw.println(binding);
		} else {
			pw.println("All variables are read at least once.");
		}
	}

	@Override
	public String getName() {
		return "Variable Read Analysis";
	}
	
	private class ReadCheckVisitor extends ASTVisitor {

		private List<IVariableBinding> allVars = new ArrayList<IVariableBinding>();
		
		public List<IVariableBinding> getAllVars() {
			return this.allVars;
		}

		@Override
		public void endVisit(InfixExpression node) {
			Expression left = node.getLeftOperand();
			Expression right = node.getRightOperand();
			List extended = node.extendedOperands();
			
			// x + y + z
			this.removeRead(left);
			this.removeRead(right);
			for (Object expr : extended)
				this.removeRead((Expression) expr);
		}

		@Override
		public void endVisit(ArrayAccess node) {
			// array[0]
			Expression array = node.getArray();
			this.removeRead(array);
		}

		@Override
		public void endVisit(Assignment node) {
			Expression right = node.getRightHandSide();
			// j = this.x; j = n;
			this.removeRead(right);
		}

		@Override
		public void endVisit(MethodInvocation node) {
			// list.size(); str.startswith("");
			Expression callee = node.getExpression();
			this.removeRead(callee);
			
			// "i" in "list.add(i)"
			List args = node.arguments();
			for (Object expr : args)
				this.removeRead((Expression) expr);
		}

		@Override
		public void endVisit(QualifiedName node) {
			// "array" in "array.length"
			Name name = node.getQualifier();
			this.removeRead(name);
		}

		@Override
		public void endVisit(FieldDeclaration node) {
			for (Object varDecl : node.fragments()) {
				VariableDeclarationFragment fragment = (VariableDeclarationFragment) varDecl;
				IVariableBinding binding = fragment.resolveBinding();
				this.allVars.add(binding);
			}
		}

		@Override
		public void endVisit(VariableDeclarationStatement node) {
			for (Object varDecl : node.fragments()) {
				VariableDeclarationFragment fragment = (VariableDeclarationFragment) varDecl;
				IVariableBinding binding = fragment.resolveBinding();
				this.allVars.add(binding);
				
				// int j = m; int j = this.x;
				this.removeRead(fragment.getInitializer());
			}
		}
		
		private void removeRead(Expression expr) {
			if (expr.getNodeType() == SIMPLE_NAME) {
				IBinding binding = ((SimpleName) expr).resolveBinding();
				this.allVars.remove(binding);
			} else if (expr.getNodeType() == FIELD_ACCESS) {
				IVariableBinding binding = ((FieldAccess) expr).resolveFieldBinding();
				this.allVars.remove(binding);
			}
		}
		
	}
}
