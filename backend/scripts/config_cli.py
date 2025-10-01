#!/usr/bin/env python3
"""
Configuration CLI tool for Travel Cost Estimator
"""
import argparse
import json
import sys
from pathlib import Path

# Add the parent directory to the path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent))

from utils.config_utils import ConfigManager

def main():
    parser = argparse.ArgumentParser(description="Travel Cost Estimator Configuration CLI")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate current configuration')
    validate_parser.add_argument('--json', action='store_true', help='Output in JSON format')
    
    # Summary command
    summary_parser = subparsers.add_parser('summary', help='Show configuration summary')
    summary_parser.add_argument('--json', action='store_true', help='Output in JSON format')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export configuration to file')
    export_parser.add_argument('file', help='Output file path')
    export_parser.add_argument('--format', choices=['json', 'env'], default='json', help='Export format')
    
    # Create env command
    env_parser = subparsers.add_parser('create-env', help='Create .env file from current settings')
    env_parser.add_argument('--file', default='.env', help='Output .env file path')
    
    # Check command
    check_parser = subparsers.add_parser('check', help='Check specific configuration values')
    check_parser.add_argument('key', help='Configuration key to check')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    config_manager = ConfigManager()
    
    if args.command == 'validate':
        validation = config_manager.validate_configuration()
        
        if args.json:
            print(json.dumps(validation, indent=2))
        else:
            print("Configuration Validation Results:")
            print("=" * 40)
            
            if validation['valid']:
                print("✅ Configuration is valid")
            else:
                print("❌ Configuration has errors")
            
            if validation['warnings']:
                print("\n⚠️  Warnings:")
                for warning in validation['warnings']:
                    print(f"  - {warning}")
            
            if validation['errors']:
                print("\n❌ Errors:")
                for error in validation['errors']:
                    print(f"  - {error}")
            
            if validation['recommendations']:
                print("\n💡 Recommendations:")
                for rec in validation['recommendations']:
                    print(f"  - {rec}")
    
    elif args.command == 'summary':
        summary = config_manager.get_config_summary()
        
        if args.json:
            print(json.dumps(summary, indent=2))
        else:
            print("Configuration Summary:")
            print("=" * 30)
            print(f"Environment: {summary['environment']}")
            print(f"Debug Mode: {summary['debug_mode']}")
            print(f"Log Level: {summary['log_level']}")
            
            print("\nAPI Keys:")
            for api, configured in summary['api_keys_configured'].items():
                status = "✅" if configured else "❌"
                print(f"  {api.title()}: {status}")
            
            print(f"\nDatabase: {summary['database']['type']}")
            print(f"Caching: {'Enabled' if summary['caching']['enabled'] else 'Disabled'}")
            print(f"Rate Limiting: {summary['rate_limiting']['requests_per_minute']} req/min")
            print(f"Monitoring: {'Enabled' if summary['monitoring']['enabled'] else 'Disabled'}")
    
    elif args.command == 'export':
        if args.format == 'json':
            success = config_manager.export_config(args.file)
            if success:
                print(f"✅ Configuration exported to {args.file}")
            else:
                print(f"❌ Failed to export configuration to {args.file}")
        elif args.format == 'env':
            success = config_manager.create_env_file(args.file)
            if success:
                print(f"✅ Environment file created at {args.file}")
            else:
                print(f"❌ Failed to create environment file at {args.file}")
    
    elif args.command == 'create-env':
        success = config_manager.create_env_file(args.file)
        if success:
            print(f"✅ Environment file created at {args.file}")
            print("📝 Please edit the file and add your API keys")
        else:
            print(f"❌ Failed to create environment file at {args.file}")
    
    elif args.command == 'check':
        settings = config_manager.get_settings()
        try:
            value = getattr(settings, args.key)
            print(f"{args.key}: {value}")
        except AttributeError:
            print(f"❌ Configuration key '{args.key}' not found")
            print("Available keys:")
            for key in dir(settings):
                if not key.startswith('_') and not callable(getattr(settings, key)):
                    print(f"  - {key}")

if __name__ == '__main__':
    main()

